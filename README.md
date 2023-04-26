# SmoothTracker

SmoothTracker is a Python application that visualizes mouse movements and clicks. The application captures the mouse positions, stores them, and generates an image representing the path of the mouse pointer. The color of the lines in the image is determined by the angle between consecutive points, and the user can adjust the line width.
![SmoothTracker_24h7m59s](https://user-images.githubusercontent.com/11169730/234631428-8adb75f2-0075-4018-8dbe-ab3b4bc9eb60.jpg)
![SmoothTracker_4h7m33s](https://user-images.githubusercontent.com/11169730/234692346-e446b9ed-c5f6-4015-85c4-7a703d652c7f.jpg)
![image](https://user-images.githubusercontent.com/11169730/234632191-35a23096-717a-4e3e-9bf6-5cf518f28276.png)


## Features

- Record mouse movements and clicks.
- Generate an image representing the path of the mouse pointer with colors based on the angle between consecutive points.
- Customize the line width for the generated image.
- Option to include or exclude mouse clicks in the generated image.
- Export the generated image as a PNG file with a filename based on the elapsed time.

## Usage

1. Run the SmoothTracker Python script to launch the GUI or use the `.exe` file available in the releases for Windows machines:

```
python main.py
```

2. Use the buttons in the GUI to control the mouse tracking:

- **Start Capture**: Starts capturing mouse movements and clicks.
- **Stop Capture**: Stops capturing mouse movements and clicks.
- **Reset Capture**: Resets the capture, discarding all recorded data.
- **Save Image**: Generates an image based on the captured data and saves it as a PNG file.

3. Customize the line width by entering a value in the "Line Width" input field.

4. Choose whether or not to include mouse clicks in the generated image by checking or unchecking the "Draw Mouse Clicks" checkbox.

5. The generated image will be saved in the same directory as the script, with a filename based on the elapsed time.

## Contributing

Contributions are welcome! If you'd like to contribute, please feel free to.  The code as it exists right now is extremely messy due to my inexperience with threading and making GUI apps.

## Reviews

looks safe to me, though i may have missed something of course
    -Redeye on discord

## License

SmoothTracker is released under the [GNU General Public License v3.0](https://opensource.org/licenses/GPL-3.0).
