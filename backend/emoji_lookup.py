from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os


class EmojiLookup:
    """Lookup table for emojis"""

    def __init__(self, _emojis_path="./emojis"):
        self.lookup = {}  # emoji name: [r,b,g averages]
        self.emojis_path = _emojis_path

        self._build_lookup()

    def _build_lookup(self):
        for file in os.listdir(self.emojis_path):
            path = os.path.join(self.emojis_path, file)
            img = Image.open(path)
            averages = self._compute_average_rgb(img)
            self.lookup[file] = averages

    def _compute_average_rgb(self, emoji: Image) -> tuple[float, float, float]:
        """
        Compute average rbg value of emoji to store in lookup table

        Args:
            emoji: PIL image of emoji
        Returns: 
            (r_avg, g_avg, b_avg) : tuple of np.float64
        """
        emoji = emoji.convert("RGBA")
        r, g, b, _ = emoji.split()  # split into 3 Images of type L
        r_arr = np.array(r)
        g_arr = np.array(g)
        b_arr = np.array(b)

        return (np.mean(r_arr), np.mean(g_arr), np.mean(b_arr))  # return tuple


if __name__ == "__main__":
    img = Image.open("./emojis/monkey.png")
