from torch import nn


def conv1x1(in_channels, out_channels, stride=1):
    return nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride, padding=0, bias=True)


def conv3x3(in_channels, out_channels, stride=1):
    return nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=True)


class ResBlock(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.main_branch = nn.Sequential(conv3x3(channels, channels), nn.ReLU(), conv3x3(channels, channels))

    def forward(self, x):
        return x + self.main_branch(x)


def conv_resblock_two(in_channels, out_channels, stride=1):
    return nn.Sequential(conv3x3(in_channels, out_channels, stride), nn.ReLU(), ResBlock(out_channels), ResBlock(out_channels))


def conv_resblock_one(in_channels, out_channels, stride=1):
    return nn.Sequential(conv3x3(in_channels, out_channels, stride), nn.ReLU(), ResBlock(out_channels))


def conv5x5_resblock_one(in_channels, out_channels, stride=1):
    # Kept as a 3x3 convolution to preserve the original trained architecture.
    return nn.Sequential(conv3x3(in_channels, out_channels, stride), nn.ReLU(), ResBlock(out_channels))


def conv3x3_leaky_relu(in_channels, out_channels, stride=1):
    return nn.Sequential(conv3x3(in_channels, out_channels, stride), nn.LeakyReLU(0.1))
