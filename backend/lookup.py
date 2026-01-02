from PIL import Image, ImageDraw, ImageFont
import numpy as np


class CharacterLookup:
    """
    Lookup table for character-based image reconstruction.
    Stores binary masks of a character at different rotations.
    """

    def __init__(self, character='a', rotations=None, tile_size=64):
        """
        Initialize the lookup table.

        Args:
            character: The character to use (e.g., 'a')
            rotations: List of rotation angles
            tile_size: Size of each tile in pixels
        """
        self.character = character
        self.tile_size = tile_size

        if rotations is None:
            self.rotations = [-30, -15, 0, 15, 30]
        else:
            self.rotations = rotations

        # Build the lookup table
        self.lookup = {}
        self._build_lookup()

    def _generate_character_image(self, rotation):
        """
        Generate an image of the character as aumpy array where each value
        is either 255 (white background) or 0 (black for the letter)
        """
        img = Image.new("L", size=(self.tile_size, self.tile_size), color=255)
        draw = ImageDraw.Draw(img)

        font = ImageFont.truetype("arial.ttf", 70)  # arial font

        draw.text((16, -10), self.character, font=font, fill=0)

        if rotation != 0:
            img = img.rotate(rotation, fillcolor=255)

        return np.array(img, dtype=np.float32)

    def _build_lookup(self):
        """
        Build the lookup table with all rotations
        Dictionary (key : value) = (rotation : numpy array of image)
        """
        print(f"Building lookup table for '{self.character}'...")

        for rotation in self.rotations:
            mask = self._generate_character_image(rotation)
            self.lookup[rotation] = mask
            print(f"\nRotation {rotation:3d} deg. stored")

        print(f"Lookup table complete: {len(self.lookup)} elements\n")

    def find_best_match(self, input_tile):
        """
        Find the best rotation and brightness for an input tile.

        Args:
            input_tile: numpy array of grayscale pixel values (0-255)
        Returns:
            dict with keys:
                - 'rotation': best rotation angle
                - 'brightness': average brightness of input tile
                - 'mse': the MSE value of the best match
        """
        # Ensure input is correct shape
        if input_tile.shape != (self.tile_size, self.tile_size):
            raise ValueError(
                f"Input tile shape {input_tile.shape} doesn't match tile_size {self.tile_size}")

        avg_brightness = np.mean(input_tile)

        # Normalize for better comparison
        normalized_input_tile = normalize_tile(input_tile)

        # Find best rotation by comparing pixel patterns
        best_rotation = None
        min_mse = float('inf')

        for rotation, mask in self.lookup.items():
            normalized_mask = normalize_tile(mask)
            mse = np.mean((normalized_input_tile - normalized_mask) ** 2)

            if mse < min_mse:
                min_mse = mse
                best_rotation = rotation

        return {
            'rotation': best_rotation,
            'brightness': avg_brightness,
            'mse': min_mse
        }

    def render_tile(self, rotation, brightness):
        """
        Render a tile with the character at given rotation and brightness.

        Args:
            rotation: Rotation angle (must be in self.rotations)
            brightness: Grayscale value to fill the character (0-255)

        Returns:
            PIL Image of the rendered tile
        """
        # Get the binary mask for this rotation
        mask = self.lookup[rotation]

        # Create output image: white background
        output = np.full((self.tile_size, self.tile_size), 255, dtype=np.uint8)

        # Fill the character pixels with the desired brightness
        # mask is 0 where character is, 255 where background is
        character_pixels = mask < 128  # boolean mask of where character is
        output[character_pixels] = int(brightness)

        return Image.fromarray(output, mode='L')


def normalize_tile(tile):
    tile = tile.astype(np.float32) / 255.0
    tile -= tile.mean()
    return tile


def process_image(input_image_path, output_image_path, tile_size=64, character='a'):
    """
    Convert an image to character art using a single character.

    Args:
        input_image_path: Path to input image
        output_image_path: Path to save output image
        tile_size: Size of each tile
        character: Character to use for reconstruction
    """
    # Load and convert input image to grayscale
    input_img = Image.open(input_image_path).convert('L')
    width, height = input_img.size

    # Crop image so dimensions are a multiple of the tile size
    new_width = (width // tile_size) * tile_size
    new_height = (height // tile_size) * tile_size
    input_img = input_img.crop((0, 0, new_width, new_height))

    # Calculate grid dimensions
    tiles_x = width // tile_size
    tiles_y = height // tile_size

    print(f"Input image: {width}x{height}")
    print(f"Grid: {tiles_x}x{tiles_y} tiles of size {tile_size}x{tile_size}\n")

    # Initialize lookup table
    lookup = CharacterLookup(character=character, tile_size=tile_size)

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
            tile = input_array[y_start:y_start +
                               tile_size, x_start:x_start+tile_size]

            # Find best match
            match = lookup.find_best_match(tile)

            # Render the tile
            rendered_tile = lookup.render_tile(
                match['rotation'], match['brightness'])

            # Place in output image
            output_img.paste(rendered_tile, (x_start, y_start))

            if (y * tiles_x + x) % 10 == 0:
                print(
                    f"Processing tile {y * tiles_x + x}/{tiles_x * tiles_y}...")

    # Save result
    output_img.save(output_image_path)
    print(f"\nOutput saved to {output_image_path}")


# Example usage
if __name__ == "__main__":
    # # Example 1: build lookup table and test with a single tile
    # lookup = CharacterLookup(character='a', tile_size=64)

    # test_image = Image.new("L", size=(64, 64), color=255)  # white background
    # draw = ImageDraw.Draw(test_image)

    # font = ImageFont.truetype("arial.ttf", 70)  # arial font

    # draw.text((16, -10), 'a', font=font, fill=100)

    # test_image = test_image.rotate(20, fillcolor=255, expand=False)

    # test_arr = np.array(test_image, dtype=np.float32)

    # # Create a test tile (e.g., a diagonal gradient)
    # test_tile = np.tile(np.linspace(0, 255, 64), (64, 1)).astype(np.uint8)

    # match = lookup.find_best_match(test_arr)
    # print(f"Test tile match:")
    # print(f"  Best rotation: {match['rotation']}°")
    # print(f"  Average brightness: {match['brightness']:.1f}")
    # print(f"  MSE: {match['mse']:.2f}")

    # # Render and show the result
    # result = lookup.render_tile(match['rotation'], match['brightness'])
    # result.show()

    process_image("C:\\Users\\akash\Downloads\\Akash ID pic.jpg",
                  'C:\\Users\\akash\Downloads\\output2.png', tile_size=64, character='a')
