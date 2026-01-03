from PIL import Image

# emoji png is 72x72
TILE_SIZE = 72


def resize(img: Image.Image, tile_size=TILE_SIZE) -> Image.Image:
    """
    Returns a resized image to fit nicely with the tile size
    """
    width, height = img.size
    new_width = (width//tile_size)*tile_size
    new_height = (height//tile_size)*tile_size
    return img.resize(new_width, new_height)


def tile_image(img: Image.Image, tile_size=TILE_SIZE) -> list[Image.Image]:
    tiles = []
    width, height = img.size

    for y in range(0, height, tile_size):
        for x in range(0, height, tile_size):
            box = (x, y, x + tile_size, y + tile_size)
            tile = img.crop(box)
            tiles.append(tile)
