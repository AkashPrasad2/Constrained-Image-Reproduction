from PIL import Image, ImageDraw, ImageFont


def render_image():
    img = Image.open("./emojis/monkey.png")
    img.show()


if __name__ == "__main__":
    render_image()
