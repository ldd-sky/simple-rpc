import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import AdamW
from dser.losses.laplacian import LapLoss
from dser.models.dser import DSER
import lpips
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class DSERTrainer:
    def __init__(self, args):
        self.model = DSER()
        self.args = args
        self.device()
        self.device_num = torch.cuda.device_count()
        self.is_multiple()
        self.optimG = AdamW(self.model.parameters(), lr=1e-6, weight_decay=1e-3)
        self.is_resume()
        self.lap = LapLoss()
        self.perc = lpips.LPIPS(net='alex').to(device)

    def is_multiple(self):
        if torch.cuda.device_count() > 1:
            print("Start with", torch.cuda.device_count(), "GPUs!")
            self.model = nn.DataParallel(self.model, device_ids=[0, 1])

    def is_resume(self):
        if self.args.RESUME:
            print("Start from ", self.args.RESUME_EPOCH)
            if self.args.RESUME_EPOCH % 5 == 0:
                path_checkpoint = "train/checkpoint/ckpt_" + str(self.args.RESUME_EPOCH) + ".pth"
            else:
                path_checkpoint = "train/checkpoint/ckpt.pth"

            checkpoint = torch.load(path_checkpoint)
            self.model.load_state_dict(checkpoint['net'])
            self.optimG.load_state_dict(checkpoint['optimizer'])

    def train(self):
        self.model.train()

    def eval(self):
        self.model.eval()

    def device(self):
        self.model.to(device)

    def save_model_min_loss(self, path):
        torch.save(self.model.state_dict(), '{}/min_loss.pkl'.format(path))

    def save_checkpoint(self, type, epoch):
        checkpoint = {
            "net": self.model.state_dict(),
            'optimizer': self.optimG.state_dict(),
            "epoch": epoch
        }
        if not os.path.isdir("./train/checkpoint"):
            os.mkdir("./train/checkpoint")
        if type == 'everyone':
            torch.save(checkpoint, './train/checkpoint/ckpt.pth')
        elif type == 'min_loss':
            torch.save(checkpoint, './train/checkpoint/ckpt_min_loss.pth')
        else:
            torch.save(checkpoint, './train/checkpoint/ckpt_%s.pth' % (str(epoch)))

    def Img_pyramid(self, Img):
        img_pyr = []
        img_pyr.append(Img)
        for i in range(1, 3):
            img_pyr.append(F.interpolate(Img, scale_factor=0.5 ** i, mode='bilinear'))
        return img_pyr

    def update(self, imgs, voxels, learning_rate):
        for param_group in self.optimG.param_groups:
            param_group['lr'] = learning_rate
        self.train()
        gt = imgs[:, 3:6]
        gt_list = self.Img_pyramid(gt)
        rec, Ft, img_t = self.model(imgs, voxels)
        loss = self.lap(Ft, imgs[:, 3:6]) + self.lap(img_t[0], imgs[:, 3:6]) + self.perc(img_t[0], imgs[:, 3:6]) + self.perc(
            Ft, imgs[:, 3:6]) + self.lap(img_t[1], gt_list[1]) + self.lap(img_t[2], gt_list[2]) + self.perc(rec, imgs[:, 12:15])
        self.optimG.zero_grad()
        loss = loss.mean()
        loss.backward()
        self.optimG.step()
        return rec, Ft, img_t[0], loss
