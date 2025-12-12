from PIL import Image
import numpy as np

IMG_SIZE = (150, 150)  # đúng kích thước model Kaggle

def prepare_image(img: Image.Image):
    img = img.resize(IMG_SIZE)
    x = np.array(img) / 255.0
    x = np.expand_dims(x, axis=0)
    return x
