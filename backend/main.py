# main.py
import io
import base64
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

app = FastAPI()

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "backend running"}


@app.post("/upload")
async def upload_image(image: UploadFile = File(...)):
    contents = await image.read()
    pil_image = Image.open(io.BytesIO(contents))

    # convert image to greyscale
    greyscale = pil_image.convert("L")
    greyscale.show()  # just so I can see in backend

    # Convert image to bytes
    buffer = io.BytesIO()
    greyscale.save(buffer, format="PNG")
    buffer.seek(0)

    # encode bytes to be sent to frontend
    image_bytes = buffer.read()
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")

    return {
        "filename": image.filename,
        "base64_image": encoded_image
    }
