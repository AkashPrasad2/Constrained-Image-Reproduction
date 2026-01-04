from PIL import Image

# emoji png is 72x72
TILE_SIZE = 72


class ImageProcessor:
    """Processes the image to be compared to the lookup table"""

    def __init__(self, intput_image: Image.Image, tile_size=TILE_SIZE):
        self.img = intput_image
        self.tile_size = tile_size
        self.width, self.height = self.img.size

    def resize(self):
        """resizes the image to fit nicely with the tile size"""
        self.width = (self.width//self.tile_size)*self.tile_size
        self.height = (self.height//self.tile_size)*self.tile_size
        self.img = self.img.resize((self.width, self.height))

    def tiles(self):
        """generator for the tiles of the input image"""
        for y in range(0, self.height, self.tile_size):
            for x in range(0, self.width, self.tile_size):
                box = (x, y, x + self.tile_size, y + self.tile_size)
                yield (x, y), self.img.crop(box)
