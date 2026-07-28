import argparse
import random
import numpy as np
import torch
from dser.engine.train import train
from dser.models.trainer import DSERTrainer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--epoch', default=100, type=int)
    parser.add_argument('--batch_size', default=6, type=int, help='minibatch size')
    parser.add_argument('--num_worker', default=4, type=int, help='num worker')
    parser.add_argument('--bsergb_root', type=str, required=True, help='BSERGB training-set root')
    parser.add_argument('--gopro_root', type=str, required=True, help='GoPro training-set root')
    parser.add_argument('--RESUME', action='store_true', help='resume training from a checkpoint')
    parser.add_argument('--RESUME_EPOCH', default=0, type=int, help='RESUME_EPOCH')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    seed = 1234
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = True

    model = DSERTrainer(args)
    train(model, args)


if __name__ == '__main__':
    main()
