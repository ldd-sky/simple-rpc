import os
import random

import cv2
import numpy as np
import torch
from torch.utils.data import Dataset

from dser.utils.event import EventSequence
from dser.utils.voxelization import to_voxel_grid


def random_crop_triplet(img0, gt, img1, height, width):
    """Crop an identically positioned patch from a training-frame triplet."""
    image_height, image_width, _ = img0.shape
    top = np.random.randint(0, image_height - height + 1)
    left = np.random.randint(0, image_width - width + 1)
    bottom, right = top + height, left + width
    return (
        img0[top:bottom, left:right, :],
        gt[top:bottom, left:right, :],
        img1[top:bottom, left:right, :],
        [top, left, bottom, right],
    )


class _TrainingDataset(Dataset):
    """Common sample construction for GoPro and BSERGB training scenes."""

    aug_size = (256, 256)

    def __init__(self, num_bins, scene, skip_frame):
        self.num_bins = num_bins
        self.scene = scene
        self.skip_frame = skip_frame

    def __len__(self):
        return len(self.img_names) - self.skip_frame - 1

    def get_img(self, index):
        offset = random.randint(1, self.skip_frame)
        img0 = cv2.imread(os.path.join(self.image_path, self.img_names[index]))
        gt = cv2.imread(os.path.join(self.image_path, self.img_names[index + offset]))
        img1 = cv2.imread(os.path.join(self.image_path, self.img_names[index + self.skip_frame + 1]))
        return img0, gt, img1, [index, index + offset, index + self.skip_frame + 1]

    def get_events(self, indices, crop):
        start, middle, end = indices
        before = [os.path.join(self.event_path, name) for name in self.event_names[start:middle]]
        after = [os.path.join(self.event_path, name) for name in self.event_names[middle:end]]
        return (
            EventSequence.from_npz_files(before, *self.aug_size, bsergb=self.bsergb, size=crop),
            EventSequence.from_npz_files(after, *self.aug_size, bsergb=self.bsergb, size=crop),
        )

    @staticmethod
    def _to_tensor(image):
        return torch.from_numpy(image.copy()).permute(2, 0, 1)

    def __getitem__(self, index):
        img0, gt, img1, indices = self.get_img(index)
        img0, gt, img1, crop = random_crop_triplet(img0, gt, img1, *self.aug_size)
        try:
            events_0t, events_t1 = self.get_events(indices, crop)
            if min(len(events_0t), len(events_t1)) < 10000:
                return self[random.randint(0, len(self) - 1)]
        except (IndexError, KeyError, OSError, ValueError):
            return self[random.randint(0, len(self) - 1)]

        event_0t_voxel = to_voxel_grid(events_0t, self.num_bins)
        event_t1_voxel = to_voxel_grid(events_t1, self.num_bins)
        event_1t_voxel = to_voxel_grid(events_t1.reverse(), self.num_bins)

        if random.random() < 0.5:
            img0, gt, img1 = img0[:, :, ::-1], gt[:, :, ::-1], img1[:, :, ::-1]
        if random.random() < 0.5:
            img0, gt, img1 = (cv2.rotate(image, cv2.ROTATE_180) for image in (img0, gt, img1))
            event_0t_voxel = torch.rot90(event_0t_voxel, 2, [1, 2])
            event_t1_voxel = torch.rot90(event_t1_voxel, 2, [1, 2])
            event_1t_voxel = torch.rot90(event_1t_voxel, 2, [1, 2])

        gray_images = [np.stack((cv2.cvtColor(image, cv2.COLOR_BGR2GRAY),) * 3, axis=-1)
                       for image in (img0, gt, img1)]
        images = torch.cat([*(self._to_tensor(image) for image in (img0, gt, img1)),
                            *(self._to_tensor(image) for image in gray_images)])
        voxels = torch.cat((event_0t_voxel, event_t1_voxel, event_1t_voxel))
        return images, voxels


class GoProDataset(_TrainingDataset):
    def __init__(self, num_bins, scene, skip_frame, root):
        super().__init__(num_bins, scene, skip_frame)
        self.data_path = os.path.join(root, 'train', scene)
        self.image_path = os.path.join(self.data_path, 'imgs')
        self.event_path = os.path.join(self.data_path, 'events')
        self.img_names = sorted(os.listdir(self.image_path))
        self.event_names = sorted(os.listdir(self.event_path))
        self.bsergb = False


class BSERGBDataset(_TrainingDataset):
    def __init__(self, num_bins, scene, skip_frame, root):
        super().__init__(num_bins, scene, skip_frame)
        self.data_path = os.path.join(root, scene)
        self.image_path = os.path.join(self.data_path, 'images')
        self.event_path = os.path.join(self.data_path, 'events')
        self.img_names = sorted(name for name in os.listdir(self.image_path) if not name.endswith('.txt'))
        self.event_names = sorted(os.listdir(self.event_path))
        self.bsergb = True
