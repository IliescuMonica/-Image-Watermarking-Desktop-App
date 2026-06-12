# ---------------------------- IMPORT LIBRARIES ------------------------------- #
from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.colorchooser import askcolor
from PIL import Image, ImageTk , ImageDraw , ImageFont

# ---------------------------- GLOBAL VARIABLES ------------------------------- #
selected_color = None
canvas = None
original_image = None #PIL clean photo
preview_image = None #PIL temporary photo for preview
preview_photo = None #Tkinter photo for canvas
logo_image = None

# ---------------------------- FUNCTIONS FOR LOADING IMAGES ------------------------------- #

def load_image(image_path):
    global canvas , preview_image , original_image , preview_photo

    original_image = Image.open(image_path).convert("RGBA")
    preview_image = original_image.copy()
    preview_image.thumbnail((600, 600))
    preview_photo = ImageTk.PhotoImage(preview_image)

    canvas = Canvas(window, width=preview_image.width, height=preview_image.height, bg="#f5f5f5", highlightthickness=0)
    canvas.create_image(0, 0, image=preview_photo, anchor=NW)
    canvas.image = preview_photo
    canvas.grid(row=3, column=3, rowspan=7)

def load_logo(logo_path):
    global canvas ,preview_image ,preview_photo , logo_image

    logo_image = Image.open(logo_path)
    logo_image.thumbnail((50, 50))

    refresh_preview()

# ---------------------------- FUNCTIONS FOR UPLOADING IMAGES ------------------------------- #

def upload_image():
    global canvas
    if canvas != None:
        canvas.delete("all")
    photo = askopenfilename()
    if photo:
        load_image(photo)

def upload_logo():
    logo = askopenfilename()
    if logo:
        load_logo(logo)

# ---------------------------- WATERMARK BUTTON FUNCTION ------------------------------- #

def add_watermark():
    refresh_preview()

# ---------------------------- COLOR BUTTON FUNCTION ------------------------------- #

def choose_color():
    global selected_color
    color = askcolor()
    selected_color = color[1]
    if color[1] is not None:
        selected_color = color[1]
    refresh_preview()

# ---------------------------- REFRESH FUNCTION ------------------------------- #

def refresh_preview():
    global preview_image, preview_photo

    if original_image is None:
        return

    preview_image = original_image.copy().convert("RGBA")
    preview_image.thumbnail((600, 600))

    apply_watermark(preview_image)

    preview_photo = ImageTk.PhotoImage(preview_image)

    canvas.config(width=preview_image.width, height=preview_image.height)
    canvas.delete("all")
    canvas.create_image(0, 0, image=preview_photo, anchor=NW)
    canvas.image = preview_photo

# ---------------------------- APPLY WATERMARK FUNCTION ------------------------------- #

def apply_watermark(image):
    watermark_text = watermark_text_entry.get()
    text_size_value = text_size_scale.get()
    text_thickness_value = text_thickness_scale.get() // 10
    opacity_value = watermark_opacity_scale.get()
    position_value = position_var.get()

    color_value = selected_color or "#000000"
    r = int(color_value[1:3], 16)
    g = int(color_value[3:5], 16)
    b = int(color_value[5:7], 16)
    color_with_opacity_value = (r, g, b, opacity_value)

    draw = ImageDraw.Draw(image)

    gap = 2

    if watermark_text:
        font = ImageFont.truetype("arial.ttf", text_size_value)

        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        watermark_width = bbox[2] - bbox[0]
        watermark_height = bbox[3] - bbox[1]
    else:
        font = None
        watermark_width = 0
        watermark_height = 0

    if logo_image:
        logo_width = logo_image.width
        logo_height = logo_image.height
    else:
        logo_width = 0
        logo_height = 0

    if logo_image and watermark_text:
        block_width = max(logo_width, watermark_width)
        block_height = logo_height + gap + watermark_height
    elif logo_image:
        block_width = logo_width
        block_height = logo_height
    else:
        block_width = watermark_width
        block_height = watermark_height

    block_x, block_y = get_position(
        position_value,
        image.width,
        image.height,
        block_width,
        block_height
    )

    if logo_image:
        logo_x = block_x + (block_width - logo_width) // 2
        logo_y = block_y

        image.paste(logo_image, (logo_x, logo_y), logo_image)

    if watermark_text:
        watermark_x = block_x + (block_width - watermark_width) // 2

        if logo_image:
            watermark_y = block_y + logo_height + gap
        else:
            watermark_y = block_y

        draw.text(
            (watermark_x, watermark_y),
            watermark_text,
            fill=color_with_opacity_value,
            font=font,
            stroke_width=text_thickness_value,
            stroke_fill=color_with_opacity_value
        )
    return image
# ---------------------------- GET POSITION BUTTONS FUNCTION ------------------------------- #

def get_position(position, image_width, image_height, watermark_width, watermark_height):
    padding = 20

    positions_coordinates = {
        "Top Left": (padding, padding),
        "Top": ((image_width - watermark_width) // 2, padding),
        "Top Right": (image_width - watermark_width - padding, padding),
        "Left": (padding, (image_height - watermark_height) // 2),
        "Center": ((image_width - watermark_width) // 2, (image_height - watermark_height) // 2),
        "Right": (image_width - watermark_width - padding, (image_height - watermark_height) // 2),
        "Bottom Left": (padding, image_height - watermark_height - padding),
        "Bottom": ((image_width - watermark_width) // 2, image_height - watermark_height - padding),
        "Bottom Right": (image_width - watermark_width - padding, image_height - watermark_height - padding),
    }
    return positions_coordinates.get(position, positions_coordinates["Center"])

# ---------------------------- SAVE BUTTON FUNCTION ------------------------------- #

def save_project():

    if original_image is None:
        return
    final_photo = original_image.copy().convert("RGBA")
    final_photo = apply_watermark(final_photo)
    save_path = asksaveasfilename(
        defaultextension=".png",
        filetypes=[
            ("PNG Image", "*.png"),
            ("JPEG Image", "*.jpg")
        ]
    )

    if save_path:
        if save_path.lower().endswith(".jpg") or save_path.lower().endswith(".jpeg"):
            final_photo = final_photo.convert("RGB")

    if save_path:
        final_photo.save(save_path)

# ---------------------------- UI SETUP ------------------------------- #

window = Tk()
window.title("Image Watermarking Desktop Application")
window.config(bg="#f5f5f5",padx=30, pady=30)

upload_image_button = Button(window, text="Open Image", bg="#f5f5f5",command=upload_image)
upload_image_button.grid(row=0, column=0)

upload_logo_button = Button(window, text="Add Logo", bg="#f5f5f5",command=upload_logo)
upload_logo_button.grid(row=0, column=1)

watermark_label = Label(window, text="Watermark:", bg="#f5f5f5")
watermark_label.grid(row=2, column=0)
watermark_text_entry = Entry(window,width=30)
watermark_text_entry.grid(row=2, column=1)
add_watermark_button = Button(window,text="Add Watermark", bg="#f5f5f5",command=add_watermark)
add_watermark_button.grid(row=2, column=2)

text_size = Label(window, text="Text Size:", bg="#f5f5f5")
text_size.grid(row=3, column=0)
text_size_scale = Scale(window, from_=0, to=100, orient=HORIZONTAL,command=lambda value: refresh_preview())
text_size_scale.grid(row=3, column=1)

text_thickness = Label(window, text="Text Thickness:", bg="#f5f5f5")
text_thickness.grid(row=4, column=0)
text_thickness_scale = Scale(window, from_=0, to=100, orient=HORIZONTAL,command=lambda value: refresh_preview())
text_thickness_scale.grid(row=4, column=1)

watermark_opacity = Label(window, text="Watermark Opacity:", bg="#f5f5f5")
watermark_opacity.grid(row=5, column=0)
watermark_opacity_scale = Scale(window, from_=0, to=255, orient=HORIZONTAL,command=lambda value: refresh_preview())
watermark_opacity_scale.grid(row=5, column=1)

text_color = Label(window, text="Choose color:", bg="#f5f5f5")
text_color.grid(row=6, column=0)
text_color_button = Button(window,text="Select color", width=25, height=1,command=choose_color)
text_color_button.grid(row=6, column=1)

watermark_position = Label(window, text="Select Watermark Position:", bg="#f5f5f5")
watermark_position.grid(row=7, column=1)

position_var = StringVar(value="Center")
positions = [
    "Top Left",
    "Top",
    "Top Right",
    "Left",
    "Center",
    "Right",
    "Bottom Left",
    "Bottom",
    "Bottom Right"
]
for i in range(len(positions)):

    label_box = Radiobutton(text = positions[i],
                    variable = position_var,
                    value = positions[i],
                    height = 2,
                    width = 10,
                    command=refresh_preview)
    label_box.grid(row = 8+(i//3), column = 0+(i%3))

save_button = Button(window, text="Save Image", bg="#f5f5f5",command=save_project)
save_button.grid(row=11, column=1)

window.mainloop()