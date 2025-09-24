This is a python tool for capturing images automatically by periodic check whether the pixels in the designate have been changed.
20250924 News! Now this tool can perform speech recognition using Alibaba Cloud's real-time speech recognition model.

The exe program can be found in the releas page: [Releases · ChenChenGith/Video_PPT_capture](https://github.com/ChenChenGith/Video_PPT_capture/releases)

Requirment:

- Python>=3.8
- pillow>=10.4.0
- screeninfo>=0.8.1
- dashscope>=1.24.5
- pyaudio>=0.2.14

# Usage:

![alt text](assert/help_image.png)

## The float window for function state

The first line displays the status of the screenshot capture function:

- The left indicator S-M turns red to show it is currently monitoring the selected area.
- The right indicator S-C turns red if a screenshot has been taken.

The second line displays the status of the speech recognition function:

- The left indicator Mic turns red to show it is currently listening to microphone input.
- The right indicator Mix turns red if it is currently monitoring stereo mix audio; if the Mix indicator is gray, stereo mix is unavailable.

## LLM service for voice recognition

This feature uses the real-time speech recognition model provided by Alibaba Cloud: paraformer-realtime-v2, so an API key is required for connection.

Model page: https://bailian.console.aliyun.com/?tab=model#/model-market/detail/paraformer-realtime-v2

API Key application page: https://bailian.console.aliyun.com/?tab=model#/api-key

New users are entitled to a free trial of 10 hours. If you choose the paid version, the price is only 0.86 RMB per hour (0.12 USD)!

Once an API key has been entered, it will be automatically saved in a text file in the root directory of the program and will be automatically loaded when the program is opened again.

# Update

## 20250924

The voice recognition feature has been added.

Optimizations have been made to the interface and storage paths.

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
