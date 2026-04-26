import torch
import torch.nn as nn
import torch.nn.functional as F

# =============================================================================
# SQUEEZE-AND-EXCITATION (SE) BLOCK
# =============================================================================
# The SE block performs feature recalibration by explicitly modelling
# interdependencies between channels.
#
# Operation flow:
#   1. SQUEEZE: Global Average Pooling collapses spatial dimensions (H x W)
#      into a single value per channel, producing a channel descriptor.
#   2. EXCITATION: Two fully-connected layers with reduction ratio `r`
#      learn a non-linear interaction between channels.
#   3. SCALE: The learned per-channel weights (0..1 via Sigmoid) are
#      multiplied back to the original feature map, emphasizing informative
#      channels and suppressing weak ones.
# =============================================================================

class SEBlock(nn.Module):
    """
    Squeeze-and-Excitation block (Hu et al., CVPR 2018).

    Args:
        channels   : Number of input/output channels (C).
        reduction  : Reduction ratio r for the bottleneck FC layer.
                     Default r=16 balances capacity and computational cost.
    """
    def __init__(self, channels, reduction=16):
        super(SEBlock, self).__init__()
        # Squeeze: Global Average Pooling -> 1x1xC
        self.pool = nn.AdaptiveAvgPool2d(1)

        # Excitation: FC(C/r) -> ReLU -> FC(C) -> Sigmoid
        self.fc = nn.Sequential(
            nn.Linear(channels, channels // reduction, bias=True),
            nn.ReLU(inplace=True),
            nn.Linear(channels // reduction, channels, bias=True),
            nn.Sigmoid()
        )

    def forward(self, x):
        """
        Forward pass.
        Input  : (N, C, H, W)
        Output : (N, C, H, W)  — same spatial dims, reweighted channels.
        """
        b, c, _, _ = x.size()

        # Squeeze
        y = self.pool(x).view(b, c)

        # Excitation
        y = self.fc(y).view(b, c, 1, 1)

        # Scale
        return x * y.expand_as(x)


# =============================================================================
# BASIC RESIDUAL BLOCK (Standard ResNet-18 / ResNet-34)
# =============================================================================
# Two 3x3 convolutions with BatchNorm and ReLU.
# Shortcut connection preserves gradient flow during backpropagation,
# enabling training of very deep networks.
# =============================================================================

class BasicBlock(nn.Module):
    """
    Standard ResNet BasicBlock (He et al., CVPR 2016).
    Expansion = 1 (output channels == intermediate channels).
    """
    expansion = 1

    def __init__(self, in_channels, out_channels, stride=1, downsample=None):
        super(BasicBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, stride=stride,
                               padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)

        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, padding=1,
                               bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)

        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        identity = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        if self.downsample is not None:
            identity = self.downsample(x)

        out += identity          # residual addition
        out = self.relu(out)
        return out


class BasicBlock_SE(nn.Module):
    """
    ResNet BasicBlock augmented with a Squeeze-and-Excitation block.
    The SE module is inserted AFTER the residual addition and final ReLU,
    recalibrating the fused feature map before passing to the next stage.
    """
    expansion = 1

    def __init__(self, in_channels, out_channels, stride=1, downsample=None,
                 reduction=16):
        super(BasicBlock_SE, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, stride=stride,
                               padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)

        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, padding=1,
                               bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)

        self.se = SEBlock(out_channels, reduction=reduction)

        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        identity = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        if self.downsample is not None:
            identity = self.downsample(x)

        out += identity
        out = self.relu(out)

        # SE recalibration on the fused feature map
        out = self.se(out)
        return out


# =============================================================================
# RESNET-18 BACKBONE (Standard — NO SE)
# =============================================================================
# Baseline architecture for ablation study in the IEEE paper.
# =============================================================================

class ResNet18(nn.Module):
    """
    Standard ResNet-18 classifier.
    Uses BasicBlock (no SE) for fair comparison against SE-ResNet.
    """
    def __init__(self, num_classes=3, zero_init_residual=False):
        super(ResNet18, self).__init__()
        self.in_channels = 64

        # Initial 7x7 stem (reduces spatial dims by 4x)
        self.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3,
                               bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)

        # Residual layers: [2, 2, 2, 2] blocks for ResNet-18
        self.layer1 = self._make_layer(BasicBlock, 64,  2, stride=1)
        self.layer2 = self._make_layer(BasicBlock, 128, 2, stride=2)
        self.layer3 = self._make_layer(BasicBlock, 256, 2, stride=2)
        self.layer4 = self._make_layer(BasicBlock, 512, 2, stride=2)

        # Classification head
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512 * BasicBlock.expansion, num_classes)

        # Kaiming initialization
        self._initialize_weights(zero_init_residual)

    def _make_layer(self, block, out_channels, num_blocks, stride=1):
        downsample = None
        if stride != 1 or self.in_channels != out_channels * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.in_channels, out_channels * block.expansion,
                          kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels * block.expansion),
            )
        layers = []
        layers.append(block(self.in_channels, out_channels, stride, downsample))
        self.in_channels = out_channels * block.expansion
        for _ in range(1, num_blocks):
            layers.append(block(self.in_channels, out_channels))
        return nn.Sequential(*layers)

    def _initialize_weights(self, zero_init_residual):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out',
                                        nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                if zero_init_residual and m.weight is not None:
                    nn.init.constant_(m.weight, 0)
                else:
                    nn.init.constant_(m.weight, 1)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        return x


# =============================================================================
# RESNET-18 + SE BACKBONE (Proposed Architecture for IEEE Paper)
# =============================================================================
# Identical to ResNet-18 except BasicBlock is replaced by BasicBlock_SE.
# SE blocks are inserted after every residual block, providing
# channel-wise attention without significantly increasing parameters.
# =============================================================================

class ResNet18_SE(nn.Module):
    """
    ResNet-18 with Squeeze-and-Excitation blocks (SE-ResNet-18).
    Proposed architecture for strawberry leaf disease classification.
    """
    def __init__(self, num_classes=3, reduction=16, zero_init_residual=False):
        super(ResNet18_SE, self).__init__()
        self.in_channels = 64

        self.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3,
                               bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)

        # SE-augmented residual layers
        self.layer1 = self._make_layer(BasicBlock_SE, 64,  2, stride=1,
                                       reduction=reduction)
        self.layer2 = self._make_layer(BasicBlock_SE, 128, 2, stride=2,
                                       reduction=reduction)
        self.layer3 = self._make_layer(BasicBlock_SE, 256, 2, stride=2,
                                       reduction=reduction)
        self.layer4 = self._make_layer(BasicBlock_SE, 512, 2, stride=2,
                                       reduction=reduction)

        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512 * BasicBlock_SE.expansion, num_classes)

        self._initialize_weights(zero_init_residual)

    def _make_layer(self, block, out_channels, num_blocks, stride=1,
                    reduction=16):
        downsample = None
        if stride != 1 or self.in_channels != out_channels * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.in_channels, out_channels * block.expansion,
                          kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels * block.expansion),
            )
        layers = []
        layers.append(block(self.in_channels, out_channels, stride,
                            downsample, reduction))
        self.in_channels = out_channels * block.expansion
        for _ in range(1, num_blocks):
            layers.append(block(self.in_channels, out_channels,
                                reduction=reduction))
        return nn.Sequential(*layers)

    def _initialize_weights(self, zero_init_residual):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out',
                                        nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                if zero_init_residual and m.weight is not None:
                    nn.init.constant_(m.weight, 0)
                else:
                    nn.init.constant_(m.weight, 1)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        return x


# =============================================================================
# LIGHTWEIGHT RESNET9 + SE (Original Project Model)
# =============================================================================
# Smaller variant for rapid inference on CPU/edge devices.
# =============================================================================

def conv_block(in_channels, out_channels, pool=False):
    layers = [
        nn.Conv2d(in_channels, out_channels, 3, padding=1, bias=True),
        nn.BatchNorm2d(out_channels),
        nn.ReLU(inplace=True)
    ]
    if pool:
        layers.append(nn.MaxPool2d(2))
    return nn.Sequential(*layers)


class ResNet9_SE(nn.Module):
    """
    Lightweight ResNet-9 with SE blocks.
    Optimized for faster training and inference on modest hardware.
    """
    def __init__(self, num_classes=3, reduction=16):
        super().__init__()
        self.conv1 = conv_block(3, 64)
        self.conv2 = conv_block(64, 128, pool=True)

        self.res1 = nn.Sequential(
            conv_block(128, 128),
            conv_block(128, 128)
        )
        self.se1 = SEBlock(128, reduction=reduction)

        self.conv3 = conv_block(128, 256, pool=True)
        self.conv4 = conv_block(256, 512, pool=True)

        self.res2 = nn.Sequential(
            conv_block(512, 512),
            conv_block(512, 512)
        )
        self.se2 = SEBlock(512, reduction=reduction)

        self.classifier = nn.Sequential(
            nn.AdaptiveMaxPool2d(1),
            nn.Flatten(),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.res1(x) + x
        x = self.se1(x)
        x = self.conv3(x)
        x = self.conv4(x)
        x = self.res2(x) + x
        x = self.se2(x)
        x = self.classifier(x)
        return x


# =============================================================================
# MODEL FACTORY
# =============================================================================

MODEL_REGISTRY = {
    "resnet18":      ResNet18,
    "resnet18_se":   ResNet18_SE,
    "resnet9_se":    ResNet9_SE,
}


def build_model(arch="resnet18_se", num_classes=3, **kwargs):
    """
    Factory function to instantiate models by name.

    Args:
        arch        : One of 'resnet18', 'resnet18_se', 'resnet9_se'.
        num_classes : Number of output classes (default 3 for strawberry).
        **kwargs    : Extra arguments passed to the model constructor.
    """
    if arch not in MODEL_REGISTRY:
        raise ValueError(f"Unknown architecture '{arch}'. Choose from: "
                         f"{list(MODEL_REGISTRY.keys())}")
    return MODEL_REGISTRY[arch](num_classes=num_classes, **kwargs)


if __name__ == "__main__":
    # Quick sanity check
    dummy = torch.randn(2, 3, 224, 224)
    for name, cls in MODEL_REGISTRY.items():
        m = cls(num_classes=3)
        out = m(dummy)
        params = sum(p.numel() for p in m.parameters())
        print(f"{name:12s} | Output: {out.shape} | Params: {params:,}")

