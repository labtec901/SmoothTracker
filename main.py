import time
import threading
from tkinter import *
from tkinter.ttk import *
import pyautogui
from PIL import Image, ImageDraw
from screeninfo import get_monitors
import math
from pynput import mouse
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import roma_cmap

resolution = 5  # Time resolution in milliseconds
radius_threshold = 5  # Number of pixels the new value has to change in the mouse recording loop to be stored.

scale_factor = 2  # Scaling factor for image resolution
supersampling_factor = 2  # Anti Ailising At the end

line_width = 4
click_point_width_multiple = 4

# Get total screen dimensions and scale them
total_width = sum(m.width for m in get_monitors()) * scale_factor * supersampling_factor
total_height = max(m.height for m in get_monitors()) * scale_factor * supersampling_factor

# Create an empty black image
image = Image.new("RGB", (total_width, total_height), "black")
draw = ImageDraw.Draw(image)

capturing = False
mouse_positions = []
click_positions = []
elapsed_time = 0
start_time = None



def angle_between_points(point1, point2):
    # Calculate the differences in the x and y coordinates
    delta_x = point2[0] - point1[0]
    delta_y = point2[1] - point1[1]

    # Calculate the angle using the atan2 function and convert it to degrees
    angle = math.degrees(math.atan2(delta_y, delta_x))

    return angle

# Function to capture mouse positions
def capture_mouse_positions():
    global capturing, mouse_positions, start_time, elapsed_time

    while True:
        if capturing:
            # Scale mouse positions by the scale factor
            x, y = pyautogui.position()
            scaled_x, scaled_y = x * scale_factor * supersampling_factor, y * scale_factor * supersampling_factor

            if not mouse_positions or math.dist((scaled_x, scaled_y),
                                                mouse_positions[-1][:2]) > radius_threshold * scale_factor * supersampling_factor:
                if mouse_positions:
                    angle = angle_between_points(mouse_positions[-1][:2], [scaled_x, scaled_y])
                    mouse_positions.append((scaled_x, scaled_y, angle))
                else:
                    mouse_positions.append((scaled_x, scaled_y, 0))
            time.sleep(resolution / 1000)
            if start_time:
                elapsed_time = time.time() - start_time
            else:
                elapsed_time = 0
            update_timer_label()
        else:
            time.sleep(resolution / 1000)


def capture_mouse_clicks():
    global click_positions, listener

    def on_click(x, y, button, pressed):
        if pressed:
            scaled_x, scaled_y = x * scale_factor * supersampling_factor, y * scale_factor * supersampling_factor
            click_positions.append((scaled_x, scaled_y))

    # with mouse.Listener(on_click=on_click) as listener:
    #     listener.join()


    listener = mouse.Listener(
        on_click=on_click)
    listener.start()
    return listener


def start_capture():
    global capturing, start_time
    capture_mouse_clicks()
    if not capturing:
        capturing = True
        if start_time is None:
            start_time = time.time()
        update_status_label()


def stop_capture():
    global capturing, start_time, elapsed_time, listener
    listener.stop()
    if capturing:
        capturing = False
        elapsed_time = time.time() - start_time
        update_status_label()


def reset_capture():
    global capturing, mouse_positions, elapsed_time, start_time, image, draw, click_positions
    stop_capture()
    mouse_positions = []
    click_positions = []
    elapsed_time = 0
    start_time = None
    image = Image.new("RGB", (total_width, total_height), "black")
    draw = ImageDraw.Draw(image)
    update_timer_label()


def save_image():
    global image, mouse_positions, elapsed_time, draw, click_positions

    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = int(elapsed_time % 60)
    image = image.resize((total_width // 2, total_height // 2), Image.BILINEAR)
    filename = "SmoothTracker_{}h{}m{}s.png".format(hours, minutes, seconds)

    def popupmsg(msg):
        popup = Tk()
        popup.wm_title("Image Complete")

        # Center the message
        label = Label(popup, text=msg, anchor='center', justify='center')
        label.pack(expand=True, fill="both", padx=10, pady=10)

        B1 = Button(popup, text="Okay", command=popup.destroy)
        B1.pack(side='bottom', pady=5, padx=(5, 5), fill="x")

        # Disable resizing
        popup.resizable(False, False)

        # Remove minimize and maximize buttons
        popup.attributes('-toolwindow', True)

        popup.mainloop()

    print("Saving image...")
    image.save(filename, "PNG")
    print("Done! Image saved as '{}'".format(filename))

    image = Image.new("RGB", (total_width, total_height), "black")
    draw = ImageDraw.Draw(image)
    popupmsg(
        f"Done! Image saved as \"{filename}\"" + "\n\n" + f"There were {len(mouse_positions)} mouse positions stored" + "\n" + f"There were {len(click_positions)} click positions stored")


def draw_positions():
    global image, draw, mouse_positions, click_positions, progress_bar, root, line_width
    progress_bar.pack(padx=(5, 5), expand=True, fill="x", anchor="w")

    def shift_cmap(cmap, frac):
        """Shifts a colormap by a certain fraction.

        Keyword arguments:
        cmap -- the colormap to be shifted. Can be a colormap name or a Colormap object
        frac -- the fraction of the colorbar by which to shift (must be between 0 and 1)
        """
        N = 256
        if isinstance(cmap, str):
            cmap = plt.get_cmap(cmap)
        n = cmap.name
        x = np.linspace(0, 1, N)
        out = np.roll(x, int(N * frac))
        new_cmap = matplotlib.colors.LinearSegmentedColormap.from_list(f'{n}_s', cmap(out))
        return new_cmap

    cmap_list = roma_cmap.cmap_list

    def angle_to_color(angle):
        norm_angle = int((abs(angle) / 180) * 255)  # Get a position in the color wheel from the angle

        # Get the color corresponding to the normalized angle
        color = cmap_list[norm_angle]
        return tuple(int(x * 255) for x in color[:3])

    def update_progress_bar(i):
        progress_bar["value"] = (i / (len(mouse_positions) - 1)) * 100
        root.update_idletasks()

    print(f"There were {len(mouse_positions)} mouse positions stored")
    for i in range(1, len(mouse_positions)):
        color = angle_to_color(mouse_positions[i][2])

        draw.line((mouse_positions[i - 1][:2], mouse_positions[i][:2]), fill=color,
                  width=line_width.get())

        # Fake rounded ends
        def circle(draw, center, radius, fill):
            draw.ellipse(
                (center[0] - radius + 1, center[1] - radius + 1, center[0] + radius - 1, center[1] + radius - 1),
                fill=fill, outline=None)

        circle(draw, mouse_positions[i - 1][:2], line_width.get() / 2, color)

        if i % int(len(mouse_positions) / 20) == 0:
            root.after(1, update_progress_bar(i))

    print(f"There were {len(click_positions)} click positions stored")
    if check_var.get():
        for pos in click_positions:
            draw.ellipse(
                [(pos[0] - line_width.get() * click_point_width_multiple,
                  pos[1] - line_width.get() * click_point_width_multiple),
                 (pos[0] + line_width.get() * click_point_width_multiple,
                  pos[1] + line_width.get() * click_point_width_multiple)],
                fill="red")
    progress_bar["value"] = 0
    progress_bar.pack_forget()


def update_status_label():
    if capturing:
        status_label.config(text="Status: Capturing")
    else:
        status_label.config(text="Status: Not Capturing")


def update_timer_label():
    timer_label.config(
        text="Elapsed Time: {}h{}m{}s".format(int(elapsed_time // 3600), int((elapsed_time % 3600) // 60),
                                              int(elapsed_time % 60)))


def main():
    global mouse_positions, status_label, timer_label, root, progress_bar

    # Start the mouse position capture thread
    capture_thread = threading.Thread(target=capture_mouse_positions)
    capture_thread.daemon = True
    capture_thread.start()

    # Create a tkinter GUI
    root = Tk()
    root.title("SmoothTracker Mouse Visualization")
    root.geometry("400x180")
    root.minsize(400, 180)

    # Add top buttons in a Frame
    top_buttons_frame = Frame(root)
    top_buttons_frame.pack(pady=5, padx=(5, 0), fill="x")

    start_button = Button(top_buttons_frame, text="Start Capture", command=start_capture)
    start_button.pack(side="left", padx=5, expand=True, fill="x")

    stop_button = Button(top_buttons_frame, text="Stop Capture", command=stop_capture)
    stop_button.pack(side="left", padx=5, expand=True, fill="x")

    reset_button = Button(top_buttons_frame, text="Reset Capture", command=reset_capture)
    reset_button.pack(side="left", padx=5, expand=True, fill="x")

    # Add labels in a separate Frame
    labels_frame = Frame(root)
    labels_frame.pack(pady=5, padx=(5, 0), fill="x")

    status_label = Label(labels_frame, text="Status: Not Capturing", anchor='w')
    status_label.pack(side="left", pady=5, padx=(5, 0))

    timer_label = Label(labels_frame, text="Elapsed Time: 0h0m0s", anchor='w')
    timer_label.pack(side="right", pady=5, padx=(0, 5))

    # Add Save Image button in a separate Frame
    save_button_frame = Frame(root)
    save_button_frame.pack(side='bottom', pady=5, fill="x")

    save_button = Button(save_button_frame, text="Save Image", command=lambda: [draw_positions(), save_image()])
    save_button.pack(pady=5, padx=(5, 5), expand=True, fill="x", anchor="s")

    # Add progress bar in a separate Frame
    progress_bar_frame = Frame(root)
    progress_bar_frame.pack(side='bottom', fill="x")

    progress_bar = Progressbar(progress_bar_frame, mode='determinate', maximum=100, value=0)
    progress_bar.pack(padx=(5, 5), expand=True, fill="x", anchor="w")
    progress_bar.pack_forget()

    # Create a BooleanVar variable to hold the checkbox state
    global check_var
    check_var = BooleanVar()
    check_var.set(True)

    # Add labels in a separate Frame
    controls_frame = Frame(root)
    controls_frame.pack(pady=5, padx=(5, 0), fill="x")
    # Create the Checkbutton widget
    checkbox = Checkbutton(controls_frame, text="Draw Mouse Clicks", variable=check_var)
    checkbox.pack(padx=(5, 5), expand=True, fill="x", side="left")

    # Create a frame for the "Line Width" input and label
    line_width_frame = Frame(controls_frame)
    line_width_frame.pack(anchor="e")

    line_width_label = Label(line_width_frame, text="Line Width (default: 4)")
    line_width_label.pack(side="left")

    global line_width
    line_width = IntVar()
    line_width.set(4)
    line_width_input = Entry(line_width_frame, textvariable=line_width, width=5)
    line_width_input.pack(side="left", padx=(5, 5))

    # Run the tkinter GUI
    root.mainloop()


if __name__ == "__main__":
    main()
