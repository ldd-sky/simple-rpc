import math
import os
import time
import numpy as np
import torch
from torch.utils.data import DataLoader, ConcatDataset
import warnings

from dser.data.datasets import GoProDataset, BSERGBDataset

warnings.filterwarnings("ignore")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
log_path = 'train'


def get_learning_rate(step, args):
    if step < 2000:
        mul = step / 2000.
        return 3e-4 * mul
    else:
        mul = np.cos((step - 2000) / (args.epoch * args.step_per_epoch - 2000.) * math.pi) * 0.5 + 0.5
        return (3e-4 - 3e-6) * mul + 3e-6


def train(model, args):
    from torch.utils.tensorboard import SummaryWriter

    writer = SummaryWriter('train')
    # writer_val = SummaryWriter('validate')
    min_loss = 999
    loss_l1 = 0
    start_epoch = 0
    step = 0
    nr_eval = 0
    scenes = sorted(os.listdir(args.bsergb_root))
    dataset = BSERGBDataset(5, scenes[0], 1, args.bsergb_root)
    for scene in scenes[1:]:
        scene_dataset = BSERGBDataset(5, scene, 1, args.bsergb_root)
        dataset = ConcatDataset([dataset, scene_dataset])
    for scene in scenes:
        scene_dataset = GoProDataset(5, scene, 3, args.gopro_root)
        dataset = ConcatDataset([dataset, scene_dataset])
    train_dataloader = DataLoader(dataset, batch_size=args.batch_size, num_workers=args.num_worker,
                                  pin_memory=True,
                                  drop_last=True, shuffle=True)
    args.step_per_epoch = train_dataloader.__len__()

    print('training...')
    time_stamp = time.time()
    if args.RESUME:
        step = args.step_per_epoch * args.RESUME_EPOCH
        nr_eval = args.RESUME_EPOCH
        start_epoch = args.RESUME_EPOCH
    for epoch in range(start_epoch, args.epoch):
        for i, data in enumerate(train_dataloader):
            data_time_interval = time.time() - time_stamp
            time_stamp = time.time()
            imgs, voxels = data
            imgs = (imgs / 255.).to(device, non_blocking=True)
            voxels = voxels.to(device, non_blocking=True)
            learning_rate = get_learning_rate(step, args) * 1 / 4
            rec, Ft, pred, loss = model.update(imgs, voxels, learning_rate)
            loss = loss.item()
            train_time_interval = time.time() - time_stamp
            time_stamp = time.time()
            if step % 100 == 1:
                writer.add_scalar('learning_rate', learning_rate, step)
                writer.add_scalar('loss/l1', loss, step)
            if step % 300 == 1:
                pred = (pred.permute(0, 2, 3, 1).detach().cpu().numpy() * 255).astype('uint8')
                Ft = (Ft.permute(0, 2, 3, 1).detach().cpu().numpy() * 255).astype('uint8')
                gt = (imgs[:, 3:6].permute(0, 2, 3, 1).detach().cpu().numpy() * 255).astype('uint8')
                gray_gt = (imgs[:, 12:15].permute(0, 2, 3, 1).detach().cpu().numpy() * 255).astype('uint8')
                rec_t = (rec.permute(0, 2, 3, 1).detach().cpu().numpy() * 255).astype('uint8')
                for i in range(min(4, pred.shape[0])):
                    imgs = np.concatenate((pred[i], gt[i], Ft[i], rec_t[i], gray_gt[i]), 1)[:, :, ::-1]
                    writer.add_image(str(i) + '/img', imgs, step, dataformats='HWC')
                writer.flush()
                if min_loss >= loss:
                    min_loss = loss
                    model.save_model_min_loss(log_path)
            print('epoch:{} {}/{} time:{:.2f}+{:.2f} loss_l1:{:.4e}'.format(epoch, i, args.step_per_epoch,
                                                                            data_time_interval, train_time_interval,
                                                                            loss))
            loss_l1 = loss
            step += 1
        nr_eval += 1
        if not math.isnan(loss_l1):
            model.save_checkpoint('everyone', nr_eval)
        else:
            break
        if nr_eval % 5 == 0:
            model.save_checkpoint('not', nr_eval)
        if nr_eval % 10 == 0:
            model.save_checkpoint('not', nr_eval)
