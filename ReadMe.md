This is a python tool for capturing images automatically by periodic check whether the pixels in the designate have been changed.

The exe program can be found in the releas page: [Releases · ChenChenGith/Video_PPT_capture](https://github.com/ChenChenGith/Video_PPT_capture/releases)

Requirment:

- Python==3.8
- pillow>=10.4.0
- screeninfo>=0.8.1

# Usage:

![1737516106198](image/ReadMe/1737516106198.png)

# Update

## 20250122

Support multi-screen with any layout.

Remove Numpy to reduce the exe size (from 35M to 12M, have not release).

Modify the initial location of the float window, to let user note it.

Add a checkbox to allow user to chose whether display float window.

Add a button for opening the image save path.

# TODO:

- [X] Test on multiple displays
- [X] Allow users to config whether display float window

# Compile:

The exe program is compiled by ``pyinstaller``. To reduce the exe size, it is better to create a new environment and install necessary package.

Then use the following command to generate exe program:

```
pyinstaller -Fw -i ycy.ico --add-data "ycy.ico;." screen_capture.py
```
