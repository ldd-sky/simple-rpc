"""Reusable utilities for evaluating DSER on frame-and-event sequences."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn.functional as F

from dser.models.dser import DSER
from dser.utils.event import EventSequence
from dser.utils.voxelization import to_voxel_grid


def load_model(checkpoint_path: Path, device: torch.device) -> DSER:
    """Load a DSER checkpoint saved by the training loop."""
    checkpoint = torch.load(checkpoint_path, map_location=device)
    state_dict = checkpoint.get("net", checkpoint)
    model = DSER().to(device)
    model.load_state_dict(state_dict)
    model.eval()
    return model


def _pad_to_multiple(tensor: torch.Tensor, multiple: int = 32) -> tuple[torch.Tensor, tuple[int, int]]:
    height, width = tensor.shape[-2:]
    pad_height = (-height) % multiple
    pad_width = (-width) % multiple
    return F.pad(tensor, (0, pad_width, 0, pad_height)), (height, width)


def build_model_inputs(
    first_frame: np.ndarray,
    last_frame: np.ndarray,
    events_before: EventSequence,
    events_after: EventSequence,
    device: torch.device,
) -> tuple[torch.Tensor, torch.Tensor, tuple[int, int]]:
    """Build DSER's 18-channel image input and 15-channel event voxel input."""
    height, width = first_frame.shape[:2]
    first = torch.from_numpy(first_frame.copy()).permute(2, 0, 1).float() / 255.0
    last = torch.from_numpy(last_frame.copy()).permute(2, 0, 1).float() / 255.0
    images = torch.zeros(18, height, width)
    images[:3] = first
    images[6:9] = last

    before = to_voxel_grid(events_before, nb_of_time_bins=5)
    after = to_voxel_grid(events_after, nb_of_time_bins=5)
    reverse_after = to_voxel_grid(events_after.reverse(), nb_of_time_bins=5)
    voxels = torch.cat((before, after, reverse_after))

    images, original_size = _pad_to_multiple(images.unsqueeze(0))
    voxels, _ = _pad_to_multiple(voxels.unsqueeze(0))
    return images.to(device), voxels.to(device), original_size


@torch.inference_mode()
def predict(model: DSER, images: torch.Tensor, voxels: torch.Tensor, original_size: tuple[int, int]) -> np.ndarray:
    """Run DSER and return the full-resolution BGR prediction as uint8."""
    prediction = model(images, voxels)[2][0]
    height, width = original_size
    prediction = prediction[..., :height, :width]
    return (prediction[0].permute(1, 2, 0).clamp(0, 1).cpu().numpy() * 255).round().astype(np.uint8)


def compute_metrics(target: np.ndarray, prediction: np.ndarray) -> tuple[float, float]:
    from skimage.metrics import peak_signal_noise_ratio, structural_similarity

    psnr = peak_signal_noise_ratio(target, prediction, data_range=255)
    ssim = structural_similarity(target, prediction, channel_axis=2, data_range=255, gaussian_weights=True)
    return float(psnr), float(ssim)


def evaluate_sequence(
    model: DSER,
    scene_dir: Path,
    frame_dir: str,
    event_dir: str,
    interval: int,
    device: torch.device,
    stride: int | None = None,
    output_dir: Path | None = None,
) -> tuple[float, float, int]:
    """Evaluate every valid interpolation window in one scene.

    Each event NPZ is expected to describe one consecutive inter-frame interval.
    """
    frame_paths = sorted((scene_dir / frame_dir).glob("*"))
    event_paths = sorted((scene_dir / event_dir).glob("*.npz"))
    if len(frame_paths) < interval + 2 or len(event_paths) < interval + 1:
        return float("nan"), float("nan"), 0

    stride = stride or interval + 1
    psnrs, ssims = [], []
    for start in range(0, len(frame_paths) - interval - 1, stride):
        end = start + interval + 1
        first_frame = cv2.imread(str(frame_paths[start]), cv2.IMREAD_COLOR)
        last_frame = cv2.imread(str(frame_paths[end]), cv2.IMREAD_COLOR)
        if first_frame is None or last_frame is None:
            continue
        for target_index in range(start + 1, end):
            target = cv2.imread(str(frame_paths[target_index]), cv2.IMREAD_COLOR)
            if target is None:
                continue
            try:
                events_before = EventSequence.from_npz_files(
                    event_paths[start:target_index], *target.shape[:2]
                )
                events_after = EventSequence.from_npz_files(
                    event_paths[target_index:end], *target.shape[:2]
                )
            except (IndexError, KeyError, OSError, ValueError):
                continue
            images, voxels, original_size = build_model_inputs(
                first_frame, last_frame, events_before, events_after, device
            )
            prediction = predict(model, images, voxels, original_size)
            psnr, ssim = compute_metrics(target, prediction)
            psnrs.append(psnr)
            ssims.append(ssim)
            if output_dir is not None:
                output_dir.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(output_dir / f"{scene_dir.name}_{target_index:06d}.png"), prediction)

    if not psnrs:
        return float("nan"), float("nan"), 0
    return float(np.mean(psnrs)), float(np.mean(ssims)), len(psnrs)
