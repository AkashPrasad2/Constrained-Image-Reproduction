# main.py
import io
import os
import base64

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

from emoji_lookup import EmojiLookup
from image_processor import ImageProcessor
# from backend.renderer import render_mosaic   # later

# App setup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global config
TILE_SIZE = 72
EMOJI_DIR = "./emojis"

emoji_lookup = EmojiLookup()
print("✅ Emoji lookup initialized")


# Core Logic
def find_best_emoji(tile_averages) -> str:
    """returns the file name of the most similar emoji"""
    best_err = float("inf")
    best_emoji = None
    r, g, b = tile_averages

    for emoji, values in emoji_lookup.lookup.items():
        er, eg, eb = values
        err = (r-er)**2 + (g-eg)**2 + (b-eb)**2

        if err < best_err:
            best_emoji = emoji
            best_err = err

    return best_emoji


def process_image_to_emoji_mosaic(input_img: Image.Image) -> Image.Image:
    processor = ImageProcessor(input_img, TILE_SIZE)
    processor.resize()

    output_img = Image.new(
        "RGB", (processor.width, processor.height), (255, 255, 255))  # blank white canvas

    for (x, y), tile in processor.tiles():
        tile_averages = emoji_lookup.compute_average_rgb(tile)
        best_emoji_name = find_best_emoji(tile_averages)

        emoji_path = os.path.join(EMOJI_DIR, best_emoji_name)
        emoji_img = Image.open(emoji_path).convert("RGBA")

        output_img.paste(emoji_img, (x, y), emoji_img)

    return output_img


# status check for backend
@app.get("/")
def health_check():
    return {"status": "backend running"}


# Upload endpoint
@app.post("/upload")
async def upload_image(image: UploadFile = File(...)):
    try:
        contents = await image.read()
        pil_image = Image.open(io.BytesIO(contents)).convert("RGB")

        output_img = process_image_to_emoji_mosaic(pil_image)

        buffer = io.BytesIO()
        output_img.save(buffer, format="PNG")
        buffer.seek(0)

        encoded_image = base64.b64encode(buffer.read()).decode("utf-8")

        return {
            "filename": image.filename,
            "base64_image": encoded_image,
            "status": "success"
        }

    except Exception as e:
        print(f"❌ Error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
