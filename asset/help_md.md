# The float window for function state

The first line displays the status of the screenshot capture function:

- The left indicator S-M turns red to show it is currently monitoring the selected area.
- The right indicator S-C turns red if a screenshot has been taken.

The second line displays the status of the speech recognition function:

- The left indicator Mic turns red to show it is currently listening to microphone input.
- The right indicator Mix turns red if it is currently monitoring stereo mix audio; if the Mix indicator is gray, stereo mix is unavailable.

# LLM service for voice recognition

*****
You need to enable stereo mix on your computer to capture system audio output! Here's how:

Settings - System - Sound - All sound devices - Enable Stereo Mix
*****

This feature uses the real-time speech recognition model provided by Alibaba Cloud: paraformer-realtime-v2, so an API key is required for connection.

Model page: https://bailian.console.aliyun.com/?tab=model#/model-market/detail/paraformer-realtime-v2

API Key application page: https://bailian.console.aliyun.com/?tab=model#/api-key

New users are entitled to a free trial of 10 hours. If you choose the paid version, the price is only 0.86 RMB per hour (0.12 USD)!

Once an API key has been entered, it will be automatically saved in a text file in the root directory of the program and will be automatically loaded when the program is opened again.


# 功能状态的浮动窗口
第一行显示截图功能的状态：
- 左侧指示灯 S-M 变红，表示当前正在监控选定区域。
- 右侧指示灯 S-C 变红，表示已进行过截图操作。

第二行显示语音识别功能的状态：
- 左侧指示灯 Mic 变红，表示当前正在监听麦克风输入。
- 右侧指示灯 Mix 变红，表示当前正在监控立体声混音音频；若 Mix 指示灯为灰色，则表示立体声混音不可用。

# 语音识别的LLM服务

*****
需要启动电脑的立体声混音，才能够捕捉系统输出！具体方法：设置-系统-声音-所有声音设备-打开立体声混音
*****

本功能使用阿里云提供的实时语音识别模型：paraformer-realtime-v2，因此连接时需要API密钥。

模型页面：https://bailian.console.aliyun.com/?tab=model#/model-market/detail/paraformer-realtime-v2

申请API密钥页面：https://bailian.console.aliyun.com/?tab=model#/api-key

新用户享有10小时的免费试用。若选择付费版本，价格仅为每小时0.86人民币（0.12美元）！

一旦输入了API密钥，它将自动保存在程序根目录下的一个文本文件中，并在下次打开程序时自动加载。