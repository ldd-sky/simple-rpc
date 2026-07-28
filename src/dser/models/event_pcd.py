import torch
from torch import nn
import torchvision
import torch.nn.functional as F
from dser.models.layers import conv1x1, conv3x3, conv3x3_leaky_relu, conv5x5_resblock_one, conv_resblock_one, conv_resblock_two


def resize_2d(inputs, target_as, mode="bilinear"):
    _, _, h, w = target_as.size()
    return F.interpolate(inputs, [h, w], mode=mode, align_corners=True)


class ReferenceFusion(nn.Module):
    def __init__(self, ch_in, ch_out):
        super().__init__()
        self.conv1 = conv(ch_in, 64)
        self.conv2 = conv(ch_in + 64, 64)
        self.conv3 = conv(ch_in + 128, 64)
        self.conv4 = conv(ch_in + 192, 64)
        self.conv_last = nn.Conv2d(ch_in + 256, ch_out, 3, 1, 1)
        self.activate = torch.sigmoid

    def forward(self, x):
        x1 = torch.cat([self.conv1(x), x], dim=1)
        x2 = torch.cat([self.conv2(x1), x1], dim=1)
        x3 = torch.cat([self.conv3(x2), x2], dim=1)
        x4 = torch.cat([self.conv4(x3), x3], dim=1)
        x_out = self.conv_last(x4)
        x_out = self.activate(x_out)
        return x_out


class up(nn.Module):
    def __init__(self, inChannels, outChannels):
        super(up, self).__init__()
        self.conv1 = nn.Conv2d(inChannels, outChannels, 3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(2 * outChannels, outChannels, 3, stride=1, padding=1)

    def forward(self, x, skpCn):
        x = F.interpolate(x, scale_factor=2, mode="bilinear")
        x = F.leaky_relu(self.conv1(x), negative_slope=0.1)
        x = F.leaky_relu(self.conv2(torch.cat((x, skpCn), 1)), negative_slope=0.1)
        return x


class down(nn.Module):
    def __init__(self, inChannels, outChannels, filterSize):
        super(down, self).__init__()
        self.conv1 = nn.Conv2d(
            inChannels,
            outChannels,
            filterSize,
            stride=1,
            padding=int((filterSize - 1) / 2),
        )
        self.conv2 = nn.Conv2d(
            outChannels,
            outChannels,
            filterSize,
            stride=1,
            padding=int((filterSize - 1) / 2),
        )

    def forward(self, x):
        x = F.avg_pool2d(x, 2)
        x = F.leaky_relu(self.conv1(x), negative_slope=0.1)
        x = F.leaky_relu(self.conv2(x), negative_slope=0.1)
        return x


def conv(in_planes, out_planes, kernel_size=3, stride=1, padding=1, dilation=1):
    return nn.Sequential(
        nn.Conv2d(in_planes, out_planes, kernel_size=kernel_size, stride=stride,
                  padding=padding, dilation=dilation, bias=True),
        nn.LeakyReLU(0.1)
    )


class EventAwareReferenceReconstructor(nn.Module):
    def __init__(self, inChannels):
        super().__init__()
        self.conv1 = nn.Conv2d(inChannels, 32, 7, stride=1, padding=3)
        self.conv2 = nn.Conv2d(32, 32, 7, stride=1, padding=3)
        self.down1 = down(32, 64, 5)
        self.down2 = down(64, 128, 3)
        self.down3 = down(128, 256, 3)
        self.down4 = down(256, 512, 3)
        self.down5 = down(512, 512, 3)
        self.up1 = up(512, 512)
        self.up2 = up(512, 256)
        self.up3 = up(256, 128)
        self.up4 = up(128, 64)
        self.up5 = up(64, 32)
        self.conv3 = nn.Conv2d(32, 1, 3, stride=1, padding=1)

    def forward(self, e):
        e = F.leaky_relu(self.conv1(e), negative_slope=0.1)
        s1 = F.leaky_relu(self.conv2(e), negative_slope=0.1)
        s2 = self.down1(s1)
        s3 = self.down2(s2)
        s4 = self.down3(s3)
        s5 = self.down4(s4)
        e = self.down5(s5)
        e = self.up1(e, s5)
        e = self.up2(e, s4)
        e = self.up3(e, s3)
        e = self.up4(e, s2)
        e = self.up5(e, s1)
        rec = self.conv3(e)
        rec = torch.sigmoid(rec)
        return rec


class EventGuidedOffsetEstimator(nn.Module):
    def __init__(self, ch_in_frame, ch_in_event, ch_in_ref, prev_offset=False):
        super().__init__()
        nf = ch_in_frame * 2 + ch_in_event + ch_in_ref
        self.conv0 = nn.Sequential(
            conv1x1(nf, nf),
            nn.ReLU(),
            conv_resblock_one(nf, nf),
            conv_resblock_one(nf, nf),
        )
        num = 2*3*3
        if prev_offset:
            na = nf + num
        else:
            na = nf
        self.conv2 = nn.Sequential(
            conv3x3(na, nf),
            nn.ReLU()
        )
        self.offset = conv3x3(nf, num)
        self.mask = conv3x3(nf, num // 2)

    def forward(self, x, offset=None):
        x = self.conv0(x)
        if offset is not None:
            x = torch.cat((x, offset), 1)
        x = self.conv2(x)
        offset = self.offset(x)
        mask = self.mask(x)
        return offset, mask


class BidirectionalEPCD(nn.Module):
    def __init__(self, num_chs_frame, num_chs_event, num_chs_ref):
        super().__init__()
        self.event_encoder = EventPyramidEncoder(num_chs_event)
        self.offset_estimator = nn.ModuleList([
            EventGuidedOffsetEstimator(num_chs_frame[-1], num_chs_event[-1], num_chs_ref[-1], prev_offset=False),
            EventGuidedOffsetEstimator(num_chs_frame[-2], num_chs_event[-2], num_chs_ref[-2], prev_offset=True),
            EventGuidedOffsetEstimator(num_chs_frame[-3], num_chs_event[-3], num_chs_ref[-3], prev_offset=True)
        ])
        self.deform_conv = nn.ModuleList([
            torchvision.ops.DeformConv2d(num_chs_frame[-1], num_chs_frame[-2], 3, 1, 1),
            torchvision.ops.DeformConv2d(num_chs_frame[-2], num_chs_frame[-3], 3, 1, 1),
            torchvision.ops.DeformConv2d(num_chs_frame[-3], num_chs_frame[-3], 3, 1, 1)
        ])
        self.fusion_block = nn.ModuleList([
            conv_resblock_one(num_chs_frame[-2] + num_chs_frame[-3], num_chs_frame[-2]),
            conv_resblock_one(num_chs_frame[-2] + num_chs_frame[-3], num_chs_frame[-3])
        ])
        self.lastconv = nn.ConvTranspose2d(num_chs_frame[-3], num_chs_frame[-3], 4, 2, 1)

    def forward(self, F0_pyramid, F1_pyramid, R_pyramid, v0):
        F0_2, F0_1, F0_0 = F0_pyramid
        F1_2, F1_1, F1_0 = F1_pyramid
        R_2, R_1, R_0 = R_pyramid
        E0_2, E0_1, E0_0 = self.event_encoder(v0)

        # ------0------
        feat_t_in = torch.cat((F0_0, E0_0, R_0, F1_0), 1)
        off_0, m_0 = self.offset_estimator[0](feat_t_in)
        F0_0_ = self.deform_conv[0](F0_0, off_0, m_0)
        off_0_up = resize_2d(off_0, F0_1)

        # ------1-------
        feat_t_in = torch.cat((F0_1, E0_1, R_1, F1_1), 1)
        off_1, m_1 = self.offset_estimator[1](feat_t_in, off_0_up)
        F0_1_ = self.deform_conv[1](F0_1, off_1, m_1)
        off_1_up = resize_2d(off_1, F0_2)
        F0_0_up = resize_2d(F0_0_, F0_1)
        F0_1_ = self.fusion_block[0](torch.cat((F0_1_, F0_0_up), 1))

        # ------2-------
        feat_t_in = torch.cat((F0_2, E0_2, R_2, F1_2), 1)
        off_2, m_2 = self.offset_estimator[2](feat_t_in, off_1_up)
        F0_2_ = self.deform_conv[2](F0_2, off_2, m_2)
        F0_1_up = resize_2d(F0_1_, F0_2)
        F0_2_ = self.fusion_block[1](torch.cat((F0_2_, F0_1_up), 1))

        out = self.lastconv(F0_2_)
        return out


class KeyframePyramidEncoder(nn.Module):
    def __init__(self, num_chs):
        super().__init__()
        self.conv1 = conv5x5_resblock_one(num_chs[0], num_chs[1], stride=1)
        self.conv2 = conv5x5_resblock_one(num_chs[1], num_chs[2], stride=2)
        self.conv3 = conv5x5_resblock_one(num_chs[2], num_chs[3], stride=2)
        self.conv4 = conv5x5_resblock_one(num_chs[3], num_chs[4], stride=2)

    def forward(self, image):
        x = self.conv1(image)
        f1 = self.conv2(x)
        f2 = self.conv3(f1)
        f3 = self.conv4(f2)
        return f1, f2, f3


class EventPyramidEncoder(nn.Module):
    def __init__(self, num_chs):
        super().__init__()
        self.conv1 = conv_resblock_one(num_chs[0], num_chs[1], stride=1)
        self.conv2 = conv_resblock_one(num_chs[1], num_chs[2], stride=2)
        self.conv3 = conv_resblock_one(num_chs[2], num_chs[3], stride=2)
        self.conv4 = conv_resblock_one(num_chs[3], num_chs[4], stride=2)

    def forward(self, image):
        x = self.conv1(image)
        f1 = self.conv2(x)
        f2 = self.conv3(f1)
        f3 = self.conv4(f2)
        return f1, f2, f3


class ReferencePyramidEncoder(nn.Module):
    def __init__(self, num_chs):
        super().__init__()
        self.conv1 = conv_resblock_one(num_chs[0], num_chs[1], stride=1)
        self.conv2 = conv_resblock_one(num_chs[1], num_chs[2], stride=2)
        self.conv3 = conv_resblock_one(num_chs[2], num_chs[3], stride=2)
        self.conv4 = conv_resblock_one(num_chs[3], num_chs[4], stride=2)

    def forward(self, image):
        x = self.conv1(image)
        f1 = self.conv2(x)
        f2 = self.conv3(f1)
        f3 = self.conv4(f2)
        return f1, f2, f3


class KeyframeFeatureEncoder(nn.Module):
    def __init__(self, in_dims, nf):
        super().__init__()
        self.conv0 = conv3x3_leaky_relu(in_dims, nf)
        self.conv1 = conv_resblock_two(nf, nf)
        self.conv2 = conv_resblock_two(nf, 2 * nf, stride=2)
        self.conv3 = conv_resblock_two(2 * nf, 4 * nf, stride=2)

    def forward(self, x):
        x_ = self.conv0(x)
        f1 = self.conv1(x_)
        f2 = self.conv2(f1)
        f3 = self.conv3(f2)
        return [f1, f2, f3]


class EventFeatureEncoder(nn.Module):
    def __init__(self, in_dims, nf):
        super().__init__()
        self.conv0 = conv3x3_leaky_relu(in_dims, nf)
        self.conv1 = conv_resblock_two(nf, nf)
        self.conv2 = conv_resblock_two(nf, 2 * nf, stride=2)
        self.conv3 = conv_resblock_two(2 * nf, 4 * nf, stride=2)

    def forward(self, x):
        x_ = self.conv0(x)
        f1 = self.conv1(x_)
        f2 = self.conv2(f1)
        f3 = self.conv3(f2)
        return [f1, f2, f3]


class ReferenceFeatureEncoder(nn.Module):
    def __init__(self, in_dims, nf):
        super().__init__()
        self.conv0 = conv3x3_leaky_relu(in_dims, nf)
        self.conv1 = conv_resblock_two(nf, nf)
        self.conv2 = conv_resblock_two(nf, 2 * nf, stride=2)
        self.conv3 = conv_resblock_two(2 * nf, 4 * nf, stride=2)

    def forward(self, x):
        x_ = self.conv0(x)
        f1 = self.conv1(x_)
        f2 = self.conv2(f1)
        f3 = self.conv3(f2)
        return [f1, f2, f3]
