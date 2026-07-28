#!/usr/bin/env python3
"""Evaluate DSER on a directory of event-camera sequences."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import torch

from dser.engine.evaluation import evaluate_sequence, load_model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data_root", type=Path, required=True, help="Directory containing scene folders.")
    parser.add_argument("--checkpoint", type=Path, required=True, help="DSER checkpoint (.pth or .pkl).")
    parser.add_argument("--frame_dir", default="images", help="Frame subdirectory in each scene.")
    parser.add_argument("--event_dir", default="events", help="Event NPZ subdirectory in each scene.")
    parser.add_argument("--intervals", default="1,3,7,15", help="Comma-separated numbers of intermediate frames.")
    parser.add_argument("--stride", type=int, default=0, help="Window stride; 0 uses interval + 1.")
    parser.add_argument("--output_dir", type=Path, help="Optional directory for predicted frames.")
    parser.add_argument("--device", default="cuda", help="Torch device, for example cuda or cpu.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    device = torch.device(args.device if args.device != "cuda" or torch.cuda.is_available() else "cpu")
    model = load_model(args.checkpoint, device)
    scene_dirs = sorted(path for path in args.data_root.iterdir() if path.is_dir())
    intervals = [int(value) for value in args.intervals.split(",") if value.strip()]

    for interval in intervals:
        results = []
        for scene_dir in scene_dirs:
            output_dir = args.output_dir / f"interval_{interval}" if args.output_dir else None
            psnr, ssim, count = evaluate_sequence(
                model, scene_dir, args.frame_dir, args.event_dir, interval, device, args.stride or None, output_dir
            )
            if count:
                results.append((psnr, ssim, count))
                print(f"[{scene_dir.name}] interval={interval}: PSNR={psnr:.3f}, SSIM={ssim:.4f}, samples={count}")
        if results:
            total = sum(item[2] for item in results)
            psnr = sum(item[0] * item[2] for item in results) / total
            ssim = sum(item[1] * item[2] for item in results) / total
            print(f"[overall] interval={interval}: PSNR={psnr:.3f}, SSIM={ssim:.4f}, samples={total}")
        else:
            print(f"[overall] interval={interval}: no valid samples found")


if __name__ == "__main__":
    main()
