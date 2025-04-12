# -*- coding: utf-8 -*-
"""CV_project_Depth.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1vNmN-4KnX5J-j0eGl3jcMCzYNkQGcQUs
"""

! pip install torch torchvision opencv-python matplotlib

import cv2
import torch
import matplotlib.pyplot as plt
from torchvision.transforms import Compose, Resize, ToTensor, Normalize
from PIL import Image

# Load MiDaS model (small version for faster inference)
model = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
model.eval()  # Set to evaluation mode

# Use GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Define image preprocessing transforms
transform = Compose([
    Resize(384),  # MiDaS expects resized images
    ToTensor(),
    Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Load and preprocess the image
image_path = "IMG-20250409-WA0019.jpg"
image = Image.open(image_path).convert('RGB') 
input_image = transform(image).unsqueeze(0).to(device)  
# Predict depth
with torch.no_grad():
    depth_pred = model(input_image)

# Post-process the depth map
depth_pred = torch.nn.functional.interpolate(
    depth_pred.unsqueeze(1),
    size=image.size[::-1],
    mode="bicubic",
    align_corners=False,
).squeeze()

depth_map = depth_pred.cpu().numpy()

# Normalize for visualization
depth_map = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min())
depth_map = (depth_map * 255).astype("uint8")

# Plot results
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.imshow(image)
plt.title("Original Image")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.imshow(depth_map, cmap="inferno")
plt.title("Depth Map")
plt.axis("off")

plt.show()
