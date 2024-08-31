from PIL import Image, ImageDraw, ImageFont

def create_image(width, height, color, text=None):
    image = Image.new("RGBA", (width, height), color)
    if text:
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        draw.text(((width - text_width) // 2, (height - text_height) // 2), text, fill="white", font=font)
    return image

# Generate the bartender image (a simple blue rectangle with "B" on it)
bartender_image = create_image(50, 100, "blue", "B")
bartender_image.save("bartender.png")

# Generate the customer image (a simple red rectangle with "C" on it)
customer_image = create_image(50, 100, "red", "C")
customer_image.save("customer.png")

# Generate the mug image (a simple brown rectangle with "M" on it)
mug_image = create_image(30, 30, "brown", "M")
mug_image.save("mug.png")

# Generate the background image (a simple green background)
background_image = create_image(800, 600, "green")
background_image.save("background.png")

print("Assets generated successfully!")
