# -*- coding: utf-8 -*-
"""CV_project2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1XqwAOAc-BTRNUJDNxNtDWJ2njgMeLsna
"""

!pip install torchvision pytorch-msssim

import torch
from torch.utils.data import Dataset, DataLoader
from torchvision.transforms import ToTensor
import matplotlib.pyplot as plt

class SyntheticDepthDataset(Dataset):
    def __init__(self, size=1000, img_size=(256, 256)):
        self.img_size = img_size
        self.size = size

    def __len__(self):
        return self.size

    def __getitem__(self, idx):
        # Generate random RGB image
        rgb = torch.rand(3, *self.img_size)  # Random noise (replace with patterns if needed)

        # Generate synthetic depth map (vertical gradient)
        depth = torch.linspace(0, 1, self.img_size[0]).view(-1, 1).repeat(1, self.img_size[1]).unsqueeze(0)

        return rgb, depth

# Example visualization
dataset = SyntheticDepthDataset()
rgb, depth = dataset[0]
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.imshow(rgb.permute(1, 2, 0))
plt.title("RGB (Synthetic)")
plt.subplot(1, 2, 2)
plt.imshow(depth.squeeze(), cmap="inferno")
plt.title("Depth (Synthetic)")
plt.show()

import torch.nn as nn
from pytorch_msssim import ssim

class DepthNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(3, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.decoder = nn.Sequential(
            nn.Conv2d(128, 64, 3, padding=1),
            nn.ReLU(),
            nn.Upsample(scale_factor=2),
            nn.Conv2d(64, 1, 3, padding=1),
            nn.Upsample(scale_factor=2),
        )

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x

def depth_loss(pred, target):
    l1_loss = nn.L1Loss()(pred, target)
    ssim_loss = 1 - ssim(pred, target, data_range=1.0)
    return l1_loss + 0.5 * ssim_loss

from torch.optim import Adam

# Initialize dataset and model
train_dataset = SyntheticDepthDataset(size=1000)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
model = DepthNet().cuda()
optimizer = Adam(model.parameters(), lr=1e-4)

# Training
for epoch in range(20):
    model.train()
    total_loss = 0.0
    for rgb, depth in train_loader:
        rgb = rgb.cuda().float()
        depth = depth.cuda().float()

        optimizer.zero_grad()
        pred = model(rgb)
        loss = depth_loss(pred, depth)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"Epoch {epoch+1}/20 | Loss: {total_loss/len(train_loader):.4f}")

print("Training complete!")

# Test on a sample
model.eval()
with torch.no_grad():
    test_rgb, test_depth = train_dataset[0]
    pred_depth = model(test_rgb.unsqueeze(0).cuda()).squeeze().cpu()

# Plot results
plt.figure(figsize=(15, 5))
plt.subplot(1, 3, 1)
plt.imshow(test_rgb.permute(1, 2, 0))
plt.title("Input RGB")
plt.subplot(1, 3, 2)
plt.imshow(test_depth.squeeze(), cmap="inferno")
plt.title("True Depth")
plt.subplot(1, 3, 3)
plt.imshow(pred_depth, cmap="inferno")
plt.title("Predicted Depth")
plt.show()