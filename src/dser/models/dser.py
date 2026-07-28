import torch
from torch import nn
from dser.models.event_pcd import (BidirectionalEPCD, EventAwareReferenceReconstructor, EventFeatureEncoder,
                                   EventPyramidEncoder, KeyframeFeatureEncoder, KeyframePyramidEncoder,
                                   ReferenceFeatureEncoder, ReferenceFusion, ReferencePyramidEncoder)
from dser.models.transformer_decoder import TransformerDecoder


class DSER(nn.Module):
    def __init__(self):
        super().__init__()
        self.event_reference_reconstructor = EventAwareReferenceReconstructor(10)
        num_chs_frame = [3, 16, 32, 64, 128]
        num_chs_event = [5, 16, 32, 64, 96]
        num_chs_ref = [1, 8, 16, 32, 64]
        self.keyframe_pyramid_encoder = KeyframePyramidEncoder(num_chs_frame)
        self.reference_pyramid_encoder = ReferencePyramidEncoder(num_chs_ref)
        self.event_pcd = BidirectionalEPCD(num_chs_frame, num_chs_event, num_chs_ref)
        self.reference_fusion = ReferenceFusion(64, 3)
        unit_dim = 32
        self.scale = 3
        self.keyframe_feature_encoder = KeyframeFeatureEncoder(3, unit_dim // 4)
        self.event_feature_encoder = EventFeatureEncoder(5, unit_dim // 2)
        self.reference_feature_encoder = ReferenceFeatureEncoder(3, unit_dim // 2)
        self.transformer_decoder = TransformerDecoder(unit_dim * 2)

    def forward(self, imgs, voxels):
        img0 = imgs[:, :3]
        img1 = imgs[:, 6:9]
        v0t = voxels[:, :5]
        v1t = voxels[:, 10:15]
        rec = self.event_reference_reconstructor(voxels[:, :10])

        F0_pyramid = self.keyframe_pyramid_encoder(img0)
        F1_pyramid = self.keyframe_pyramid_encoder(img1)
        R_pyramid = self.reference_pyramid_encoder(rec)

        F0 = self.event_pcd(F0_pyramid, F1_pyramid, R_pyramid, v0t)
        F1 = self.event_pcd(F0_pyramid, F1_pyramid, R_pyramid, v1t)
        Ft = self.reference_fusion(torch.cat((F0, F1), 1))

        f_frame0 = self.keyframe_feature_encoder(img0)
        f_frame1 = self.keyframe_feature_encoder(img1)
        ref_feature = self.reference_feature_encoder(Ft)
        f_event_0t = self.event_feature_encoder(v0t)
        f_event_1t = self.event_feature_encoder(v1t)

        forward_feature = []
        backward_feature = []
        for idx in range(self.scale):
            forward_feature.append(torch.cat((f_frame0[idx], f_event_0t[idx]), dim=1))  # 24, 48, 96
            backward_feature.append(torch.cat((f_frame1[idx], f_event_1t[idx]), dim=1))

        img_t = self.transformer_decoder(forward_feature, backward_feature, ref_feature)
        rec = rec.repeat(1, 3, 1, 1)
        return rec, Ft, img_t
