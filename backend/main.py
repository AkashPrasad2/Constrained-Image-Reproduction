# main.py
import io
import base64
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import numpy as np
from backend.character_lookup import CharacterLookup

app = FastAPI()

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the lookup table once when server starts
# This avoids rebuilding it on every request
TILE_SIZE = 64
CHARACTER = 'a'
lookup_table = CharacterLookup(character=CHARACTER, tile_size=TILE_SIZE)
print("Lookup table initialized and ready!")


@app.get("/")
def health_check():
    return {"status": "backend running"}


def process_image_to_character_art(input_img, tile_size=64):
    """
    Convert a PIL image to character art and return as PIL image.

    Args:
        input_img: PIL Image in grayscale
        tile_size: Size of each tile

    Returns:
        PIL Image of the character art
    """
    width, height = input_img.size

    # Crop image so dimensions are a multiple of the tile size
    new_width = (width // tile_size) * tile_size
    new_height = (height // tile_size) * tile_size
    input_img = input_img.crop((0, 0, new_width, new_height))

    # Calculate grid dimensions
    tiles_x = new_width // tile_size
    tiles_y = new_height // tile_size

    print(f"Processing: {tiles_x}x{tiles_y} tiles")

    # Create output image
    output_img = Image.new(
        'L', (tiles_x * tile_size, tiles_y * tile_size), color=255)

    # Process each tile
    input_array = np.array(input_img)

    for y in range(tiles_y):
        for x in range(tiles_x):
            # Extract tile from input
            y_start = y * tile_size
            x_start = x * tile_size
            tile = input_array[y_start:y_start + tile_size,
                               x_start:x_start + tile_size]

            # Find best match
            match = lookup_table.find_best_match(tile)

            # Render the tile
            rendered_tile = lookup_table.render_tile(
                match['rotation'], match['brightness'])

            # Place in output image
            output_img.paste(rendered_tile, (x_start, y_start))

    return output_img


@app.post("/upload")
async def upload_image(image: UploadFile = File(...)):
    try:
        contents = await image.read()
        pil_image = Image.open(io.BytesIO(contents))

        # Convert image to grayscale
        grayscale = pil_image.convert("L")

        # Process into character art
        character_art = process_image_to_character_art(
            grayscale, tile_size=TILE_SIZE)

        # Convert to bytes for sending to frontend
        buffer = io.BytesIO()
        character_art.save(buffer, format="PNG")
        buffer.seek(0)

        # Encode as base64
        image_bytes = buffer.read()
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")

        return {
            "filename": image.filename,
            "base64_image": encoded_image,
            "status": "success"
        }

    except Exception as e:
        print(f"Error processing image: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
