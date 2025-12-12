import os
import glob
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
from concurrent.futures import ThreadPoolExecutor
import tensorflow as tf
from PIL import Image
import io
import numpy as np
import kagglehub

app = FastAPI(title="Dog vs Cat Classifier API (KaggleHub)")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL = None
executor = ThreadPoolExecutor(max_workers=2)

# -------------------------------------
# 1. Hàm tìm kiếm model đa năng (.h5, .keras, hoặc .pb)
# -------------------------------------
def find_best_model_path(root_dir):
    print(f"Searching for model in: {root_dir}")
    
    # Ưu tiên 1: Tìm file .h5 hoặc .keras (Model Keras thông thường)
    for ext in ["*.h5", "*.keras"]:
        search_path = os.path.join(root_dir, "**", ext)
        files = glob.glob(search_path, recursive=True)
        if files:
            print(f"Found Keras file: {files[0]}")
            return files[0], "keras_file"
            
    # Ưu tiên 2: Tìm saved_model.pb (TensorFlow SavedModel folder)
    search_path = os.path.join(root_dir, "**", "saved_model.pb")
    files = glob.glob(search_path, recursive=True)
    if files:
        folder_path = os.path.dirname(files[0])
        print(f"Found SavedModel folder: {folder_path}")
        return folder_path, "saved_model_folder"
        
    raise FileNotFoundError(f"Không tìm thấy model (.h5, .keras, .pb) trong {root_dir}")

# -------------------------------------
# 2. Load model thông minh
# -------------------------------------
@app.on_event("startup")
def startup_event():
    global MODEL

    print("Downloading model from KaggleHub...")
    download_path = kagglehub.model_download(
        "wafaaelhusseini/cats-vs-dogs-classifier/tensorFlow2/fine-tuned-mobilenetv2"
    )
    
    # Tìm đường dẫn và loại model
    model_path, model_type = find_best_model_path(download_path)

    print(f"Loading model type: {model_type}...")
    
    try:
        if model_type == "keras_file":
            # Load file .h5 / .keras bình thường
            MODEL = tf.keras.models.load_model(model_path)
        else:
            # Load folder SavedModel bằng TFSMLayer (Fix cho Keras 3)
            MODEL = tf.keras.layers.TFSMLayer(model_path, call_endpoint='serving_default')
            
        print("Model loaded successfully!")
    except Exception as e:
        print(f"CRITICAL ERROR loading model: {e}")
        raise e

# -------------------------------------
# Prepare image
# -------------------------------------
def prepare_image(img: Image.Image):
    img = img.resize((224, 224))
    x = np.array(img).astype("float32") / 255.0
    x = np.expand_dims(x, axis=0)
    return x

# -------------------------------------
# 3. Inference xử lý cả 2 loại đầu ra
# -------------------------------------
async def run_predict(x):
    loop = asyncio.get_running_loop()
    
    def _predict():
        # Chạy model
        outputs = MODEL(x)
        
        # Xử lý đầu ra đa dạng (Do TFSMLayer trả về dict, còn load_model trả về Tensor)
        if isinstance(outputs, dict):
            # Nếu là Dictionary (TFSMLayer)
            return list(outputs.values())[0].numpy()
        elif hasattr(outputs, 'numpy'):
            # Nếu là EagerTensor
            return outputs.numpy()
        else:
            # Nếu là Numpy array (cũ)
            return outputs

    return await loop.run_in_executor(executor, _predict)

# -------------------------------------
# Predict API
# -------------------------------------
@app.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File is not an image.")

    contents = await file.read()

    try:
        img = Image.open(io.BytesIO(contents)).convert("RGB")
    except:
        raise HTTPException(400, "Cannot load image.")

    x = prepare_image(img)
    
    preds = await run_predict(x)
    
    # Lấy score (giả sử output shape là (1, 1) hoặc (1, 2))
    # Mobilenet binary thường ra (1, 1) sigmoid hoặc (1, 2) softmax
    # Code cũ của bạn xử lý sigmoid (1 output node)
    
    if preds.shape[-1] == 1:
        score = float(preds[0][0])
        pred_label = "dog" if score >= 0.5 else "cat"
        pred_prob = score if score >= 0.5 else 1 - score
    else:
        # Trường hợp model trả về 2 lớp (softmax)
        score_cat = float(preds[0][0])
        score_dog = float(preds[0][1])
        if score_dog > score_cat:
            pred_label = "dog"
            pred_prob = score_dog
            score = score_dog
        else:
            pred_label = "cat"
            pred_prob = score_cat
            score = score_cat # Đại diện

    return JSONResponse({
        "prediction_label": pred_label,
        "prediction_prob": pred_prob,
        "raw_output": score
    })

@app.get("/")
def root():
    return {"message": "Dog vs Cat API ready. POST /predict with an image."}