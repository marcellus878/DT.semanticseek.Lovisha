import torch
import clip
from PIL import Image
import os

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)


def get_image_embedding(image_path):
    if not image_path or not os.path.exists(image_path):
        return None
    try:
        image = (
            preprocess(Image.open(image_path).convert("RGB")).unsqueeze(0).to(device)
        )
        with torch.no_grad():
            emb = model.encode_image(image)
        emb = emb / emb.norm(dim=-1, keepdim=True)
        return emb
    except Exception as e:
        print("Image embedding error:", e)
        return None


def image_similarity(path1, path2):
    e1 = get_image_embedding(path1)
    e2 = get_image_embedding(path2)
    if e1 is None or e2 is None:
        return 0.0
    return float((e1 @ e2.T).item())
