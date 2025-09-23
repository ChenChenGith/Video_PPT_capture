# Repositories url: https://github.com/ChenChenGith/Video_PPT_capture

# version: 0.1.0
# license: MIT

from PIL import ImageGrab, ImageChops, ImageStat
import time
import tkinter as tk
from tkinter import filedialog
import sys, os
from screeninfo import get_monitors
import threading
import multiprocessing

from dashscope.audio.asr import RecognitionCallback, RecognitionResult, Recognition
import dashscope
import pyaudio


def get_all_display_info():
    x, y = [], []
    for m in get_monitors():
        x.append(m.x)
        x.append(m.x + m.width)
        y.append(m.y)
        y.append(m.y + m.height)
    
    return max(x) - min(x), max(y) - min(y), min(x), min(y)

def find_stereo_mix_device(mic):
    keyword_list = ["stereo mix", "立体声混音"]
    for i in range(mic.get_device_count()):
        info = mic.get_device_info_by_index(i)
        name = info.get('name', '').lower()
        if info.get('maxInputChannels', 0) > 0:
            for kw in keyword_list:
                if kw in name:
                    # 尝试打开设备，能打开才算可用
                    try:
                        test_stream = mic.open(format=pyaudio.paInt16,
                                              channels=1,
                                              rate=16000,
                                              input=True,
                                              input_device_index=i)
                        test_stream.close()
                        return i
                    except Exception as e:
                        continue
    return None

class Capture_window_select(object):
    def __init__(self, capture_window=None):
        self.window = tk.Tk()
        self.window.overrideredirect(True)         # 隐藏窗口的标题栏
        self.window.attributes("-alpha", 0.5)      # 窗口透明度10%
        
        self.width, self.height, self.x, self.y = get_all_display_info()
        
        # self.width = self.window.winfo_screenwidth()
        # self.height = self.window.winfo_screenheight()
        self.window.geometry("{0}x{1}+{2}+{3}".format(self.width, self.height, self.x, self.y))

        self.window.bind('<Escape>', self.exit_1)
        self.window.bind('<Return>', self.exit_2)
        self.window.bind("<Button-1>", self.selection_start)  # 鼠标左键点击->显示子窗口 
        self.window.bind("<ButtonRelease-1>", self.selection_end) # 鼠标左键释放->记录最后光标的位置
        self.window.bind("<B1-Motion>", self.change_selection)   # 鼠标左键移动->显示当前光标位置

        self.canvas = tk.Canvas(self.window, width=self.width, height=self.height)
        self.canvas.pack()

        self.remember = None
        if capture_window != None:
            self.remember = capture_window
        else:
            self.remember = 0, 0, self.width, self.height

        self.canvas.create_text(self.width - 500, self.height - 500, text=f"Esc: Full-screen\nLeft click and move: select capture region\nEnter: Confirm selection", fill="red", tags="info", font=("Arial", 30))

        self.window.focus_force()
        self.window.mainloop()

    def exit_1(self, event):
        self.window.destroy()
        self.window.quit()

    def exit_2(self, event):
        try:
            self.remember = [self.start_x, self.start_y, self.end_x, self.end_y]
        except:
            pass
        self.window.destroy()
        self.window.quit()
        
    def rel2abs(self, x, y):
        return x + self.x, y + self.y
    
    def selection_start(self, event):
        self.canvas.delete("rect", "text")
        self.win_start_x = event.x
        self.win_start_y = event.y
        self.rect = self.canvas.create_rectangle(self.win_start_x, self.win_start_y, self.win_start_x, self.win_start_y, outline='red', width=2, tags="rect", dash=(4, 4))
        
        self.start_x, self.start_y = self.rel2abs(event.x, event.y)
        
        self.canvas.create_text(self.win_start_x + 35, self.win_start_y + 10, text=f"({self.start_x}, {self.start_y})", fill="red", tags="text")
    
    def selection_end(self, event):
        self.win_end_x = event.x
        self.win_end_y = event.y
        self.end_x, self.end_y = self.rel2abs(event.x, event.y)
        self.canvas.create_text(self.win_end_x - 90, self.win_end_y - 25, text=f"({self.end_x}, {self.end_y})({self.end_x-self.start_x}X{self.end_y-self.start_y})", fill="red", tags="text")
        self.canvas.create_text(self.win_end_x - 100, self.win_end_y - 10, text="Press Enter to confirm selection", fill="red", tags="text")

    def change_selection(self, event):
        self.canvas.coords(self.rect, self.win_start_x, self.win_start_y, event.x, event.y)
    
    def get_capture_window_coor(self):
        x1, y1, x2, y2 = self.remember
        return [
            min(x1, x2),
            min(y1, y2),
            max(x1, x2),
            max(y1, y2)
        ]

def get_resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Real-time speech recognition callback
class Callback(RecognitionCallback):
    def __init__(self, log_file, text_queue, stereo_mix_index=None, voice_source="stereo mix"):
        super().__init__()
        self.log_file = log_file
        self.text_queue = text_queue
        self.mic = None
        self.stream = None
        self.voice_source = voice_source
        self.stereo_mix_index = stereo_mix_index

    def on_open(self) -> None:
        self.text_queue.put(f"{self.time_str}: Speech recognition started, using {self.voice_source}.\n")
        self.mic = pyaudio.PyAudio()
        if self.voice_source == "stereo mix":            
            self.stream = self.mic.open(format=pyaudio.paInt16,
                                        channels=1,
                                        rate=16000,
                                        input=True,
                                        input_device_index=self.stereo_mix_index)
        elif self.voice_source == "mic":
            self.text_queue.put(f"{self.time_str}: Using default microphone as audio source.\n")
            self.stream = self.mic.open(format=pyaudio.paInt16,
                                        channels=1,
                                        rate=16000,
                                        input=True)

    def on_close(self) -> None:
        self.text_queue.put(f"{self.time_str}: Speech recognition from source [{self.voice_source}] stopped.\n")
        self.stream.stop_stream()
        self.stream.close()
        self.mic.terminate()
        self.stream = None
        self.mic = None

    def on_complete(self) -> None:
        self.text_queue.put(f"\n{self.time_str}: RecognitionCallback completed.\n")

    def on_error(self, message) -> None:
        self.text_queue.put(f"{self.time_str}: RecognitionCallback error: {message.message}\n")
        # Stop and close the audio stream if it is running
        if self.stream.active:
            self.stream.stop()
            self.stream.close()

    def on_event(self, result: RecognitionResult) -> None:
        sentence = result.get_sentence()
        # 只在句子结束时输出和累加，避免重复
        if RecognitionResult.is_sentence_end(sentence) and 'text' in sentence:
            self.text_queue.put(f"{self.time_str}: text from {self.voice_source}: {sentence['text']}\n")
            # 实时写入日志文件
            if self.log_file:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(sentence['text'] + '\n')

    @property
    def time_str(self):
        return time.strftime("%Y%m%d-%H%M%S", time.localtime())


def run_asr_process(log_filename, text_queue, apikey, stereo_mix_index, source="stereo mix"):
    dashscope.api_key = apikey
    callback = Callback(log_file=log_filename, text_queue=text_queue, stereo_mix_index=stereo_mix_index, voice_source=source)
    sample_rate = 16000  # 采样率
    format_pcm = 'pcm'  # 音频数据格式
    block_size = 3200  # 每次读取的帧数
    recognition = Recognition(
                model='paraformer-realtime-v2',
                format=format_pcm,
                sample_rate=sample_rate,
                semantic_punctuation_enabled=False,
                callback=callback)
    recognition.start()
    while True:
        if callback.stream:
            data = callback.stream.read(block_size, exception_on_overflow=False)
            recognition.send_audio_frame(data)
        else:
            break
    recognition.stop()


class ScreenCapture(object):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PPT in Video Capture Tool. CC:ChenChenGith@github")
        self.win_width, self.win_height = int(min(self.root.winfo_screenwidth()/1.8, 900)), int(min(self.root.winfo_screenheight(), 750))
        self.root.geometry("{0}x{1}+0+0".format(self.win_width, self.win_height))
        self.root.iconbitmap(get_resource_path("./ycy.ico"))

        # 主frame，分为左侧信息区和右侧设置区
        self.main_frame = tk.Frame(self.root)
        self.main_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # 左侧信息区
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.place(relx=0.02, rely=0.03, relwidth=0.7, relheight=0.94)
        # 上：截图信息
        tk.Label(self.left_frame, text="Screen Capture Info", anchor="w", font=("Arial", 11, "bold")).pack(fill="x")
        self.text_info = tk.Text(self.left_frame, height=18)
        self.text_info.pack(fill="x", expand=False)
        # 中：语音识别信息
        tk.Label(self.left_frame, text="Speech Recognition Info", anchor="w", font=("Arial", 11, "bold")).pack(fill="x", pady=(10,0))
        self.text_asr = tk.Text(self.left_frame, height=18)
        self.text_asr.pack(fill="both", expand=True)
        # 下：系统日志信息
        tk.Label(self.left_frame, text="System Log Info", anchor="w", font=("Arial", 11, "bold")).pack(fill="x", pady=(10,0))
        self.text_log = tk.Text(self.left_frame, height=8)
        self.text_log.pack(fill="both", expand=True)


        # 右侧设置区
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.place(relx=0.74, rely=0.03, relwidth=0.24, relheight=0.94)

        # 上：截图设置
        self.frame_cap = tk.LabelFrame(self.right_frame, text="Screen Capture Settings", font=("Arial", 10, "bold"))
        self.frame_cap.pack(fill="x", padx=2, pady=2)
        tk.Label(self.frame_cap, text="Check Interval (s)").grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        self.ety_capture_interval = tk.Entry(self.frame_cap, justify="center", width=6)
        self.ety_capture_interval.insert(0, "5")
        self.ety_capture_interval.grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        self.scb_sensitivity = tk.Scale(self.frame_cap, from_=0, to=20, orient="horizontal", label="Sensitivity (0=High)", resolution=1, length=100)
        self.scb_sensitivity.set(2)
        self.scb_sensitivity.grid(row=1, column=0, columnspan=2, sticky="ew", padx=2, pady=2)
        self.btn_window_config = tk.Button(self.frame_cap, text="Capture Window Selection", command=self.get_capture_window)
        self.btn_window_config.grid(row=2, column=0, columnspan=2, sticky="ew", padx=2, pady=2)
        tk.Label(self.frame_cap, text="Capt. Win. Info:", fg='gray').grid(row=3, column=0, sticky="ew", padx=2, pady=2)
        self.label_capture_window = tk.Label(self.frame_cap, text="None", fg="gray")
        self.label_capture_window.grid(row=3, column=1, sticky="ew", padx=2, pady=2)
        self.btn_start = tk.Button(self.frame_cap, text="Start Capture", command=self.start_capture, state="disabled")
        self.btn_start.grid(row=6, column=0, sticky="ew", padx=2, pady=2)
        self.btn_stop = tk.Button(self.frame_cap, text="Stop Capture", command=self.stop_capture, state="disabled")
        self.btn_stop.grid(row=6, column=1, sticky="ew", padx=2, pady=2)
        self.frame_cap.columnconfigure(0, weight=1)
        self.frame_cap.columnconfigure(1, weight=1)

        # 下：语音识别设置
        self.frame_asr = tk.LabelFrame(self.right_frame, text="Speech Recognition Settings", font=("Arial", 10, "bold"))
        self.frame_asr.pack(fill="x", padx=2, pady=(10,2))
        tk.Label(self.frame_asr, text="API Key").grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        self.ety_api_key = tk.Entry(self.frame_asr, show="*", width=18)
        self.ety_api_key.grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        self.btn_asr_start = tk.Button(self.frame_asr, text="Start SRS", command=self.start_asr, state="normal")
        self.btn_asr_start.grid(row=2, column=0, sticky="ew", padx=2, pady=2)
        self.btn_asr_stop = tk.Button(self.frame_asr, text="Stop SRS", command=self.stop_asr, state="disabled")
        self.btn_asr_stop.grid(row=2, column=1, sticky="ew", padx=2, pady=2)
        # 两个勾选框分别选择是否开启麦克风和立体声混音监听，默认都勾选        
        self.stereo_mix_index = None
        self._check_stereo_mix()
        self.use_microphone = tk.BooleanVar(value=True)
        self.use_stereo_mix = tk.BooleanVar(value=True if self.stereo_mix_index else False)
        self.check_microphone = tk.Checkbutton(self.frame_asr, text="Microphone", variable=self.use_microphone, command=self._swtch_btn_asr_start)
        self.check_microphone.grid(row=1, column=0, sticky="ew", padx=2, pady=2)
        self.check_stereo_mix = tk.Checkbutton(self.frame_asr, text="Stereo Mix", variable=self.use_stereo_mix, state="normal" if self.stereo_mix_index else "disabled", command=self._swtch_btn_asr_start)
        self.check_stereo_mix.grid(row=1, column=1, sticky="ew", padx=2, pady=2)

        self.frame_asr.columnconfigure(0, weight=1)
        self.frame_asr.columnconfigure(1, weight=1)


        # 控制面板：一键启动/停止
        self.frame_ctrl = tk.LabelFrame(self.right_frame, text="Control Panel", font=("Arial", 10, "bold"))
        self.frame_ctrl.pack(fill="x", padx=2, pady=(10,2))
        self.btn_all_start = tk.Button(self.frame_ctrl, text="Start All", command=self.start_all, state="normal")
        self.btn_all_start.grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        self.btn_all_stop = tk.Button(self.frame_ctrl, text="Stop All", command=self.stop_all, state="disabled")
        self.btn_all_stop.grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        self.frame_ctrl.columnconfigure(0, weight=1)
        self.frame_ctrl.columnconfigure(1, weight=1)

        # 日志保存路径
        self.frame_save_path = tk.LabelFrame(self.right_frame, text="Log Save Path", font=("Arial", 10, "bold"))
        self.frame_save_path.pack(fill="x", padx=2, pady=(10,2))
        # 两行布局：第一行为标签和路径，第二行为按钮
        tk.Label(self.frame_save_path, text=f"Last\nSaved", fg='gray').grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.label_save_path = tk.Label(self.frame_save_path, fg="gray", bd=0, text="None", anchor="w", wraplength=120)
        self.label_save_path.grid(row=0, column=1, columnspan=2, sticky="ew", padx=2, pady=2)
        self.btn_save_path_open = tk.Button(self.frame_save_path, text="Open Folder", command=self.open_save_path, state="normal")
        self.btn_save_path_open.grid(row=1, column=0, columnspan=3, sticky="ew", padx=3, pady=2)
        self.frame_save_path.columnconfigure(1, weight=1)
        self.frame_save_path.columnconfigure(2, weight=0)

        # add a help button
        self.btn_help = tk.Button(self.right_frame, text="Help", command=self.show_help)
        self.btn_help.pack(fill="x", padx=2, pady=25)

        # 退出按钮
        self.btn_sys_out = tk.Button(self.right_frame, text="Exit", command=self.sys_out)
        self.btn_sys_out.pack(side="bottom", fill="x", padx=2, pady=8)

        # 关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # 是否显示浮动窗口复选框
        self.is_show_state_window_var = tk.BooleanVar()
        self.is_show_state_window = tk.Checkbutton(self.right_frame, text="Show State Window", command=self.show_state_window, variable=self.is_show_state_window_var)
        self.is_show_state_window.select()
        self.is_show_state_window.pack(side="bottom", fill="x", padx=2, pady=2)

        self.sensitivity = None
        self.is_capturing = False
        self.is_speech_recognizing = False
        self.is_asr_queue_checking = False
        self.apikey = None
        self.capture_window = None
        self.save_path = None  
        self.im = None
        self.mouse_x, self.mouse_y = 0, 0

        self.asr_queue = multiprocessing.Queue()

        self.__init_state_window()
        self.root.mainloop()
        
    def start_all(self):
        # 启动截图和语音识别（仅UI按钮状态切换，功能后续实现）
        do_not_prapare = False
        if self.capture_window is None:
            self.text_log.insert("end", f"{self.time_str}: Please select capture window first!\n")
            self.text_log.see("end")
            do_not_prapare = True
        if not self._check_has_input_api():
            do_not_prapare = True
        if do_not_prapare:
            return
        
        if self.btn_start['state'] == 'normal':
            self.start_capture()
        if self.btn_asr_start['state'] == 'normal':
            self.start_asr()
        self.btn_all_start['state'] = 'disabled'
        self.btn_all_stop['state'] = 'normal'

    def stop_all(self):
        # 停止截图和语音识别（仅UI按钮状态切换，功能后续实现）
        if self.btn_stop['state'] == 'normal':
            self.stop_capture()
        if self.btn_asr_stop['state'] == 'normal':
            self.stop_asr()
        self.btn_all_start['state'] = 'normal'
        self.btn_all_stop['state'] = 'disabled'
   
    def select_log_path(self):
        path = filedialog.askdirectory()
        if path:
            self.ety_log_path.delete(0, "end")
            self.ety_log_path.insert(0, path)

    def _init_auto_save_dir(self):
        folder = time.strftime("%Y%m%d-%H%M%S", time.localtime())
        save_dir = get_resource_path(folder)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        self.save_path = save_dir
        self.label_save_path['text'] = self.save_path
        self.text_log.insert("end", f"{self.time_str}: Log and images will be saved to {self.save_path}\n")
        self.text_log.see("end")

    def _swtch_btn_asr_start(self):
        if self.use_microphone.get() or self.use_stereo_mix.get():
            self.btn_asr_start['state'] = 'normal'
        else:
            self.btn_asr_start['state'] = 'disabled'

    def _check_stereo_mix(self):
        mic = pyaudio.PyAudio()
        self.stereo_mix_index = find_stereo_mix_device(mic)
        if self.stereo_mix_index is None:
            self.text_log.insert("end", f"{self.time_str}: Stereo Mix not found! Please activate the stereo mix device. See help documentation for more details.\n")
            self.text_log.see("end")
        else:
            self.text_log.insert("end", f"{self.time_str}: Can use 'Stereo Mix' device (index={self.stereo_mix_index}) as audio source.\n")
            self.text_log.see("end")

    def _check_has_input_api(self):
        # 检查是否有存储的api key
        if self.apikey:
            return True
        if os.path.exists(get_resource_path("api_key.txt")):
            with open(get_resource_path("api_key.txt"), 'r') as f:
                self.apikey = f.read().strip()
            if self.apikey:
                self.text_log.insert("end", f"{self.time_str}: Loaded API Key from api_key.txt\n")
                self.text_log.insert("end", self.apikey)
                self.ety_api_key.delete(0, "end")
                self.ety_api_key.insert(0, self.apikey)
                return True

        api_key = self.ety_api_key.get().strip()
        if not api_key:
            self.text_log.insert("end", f"{self.time_str}: Please input API Key for speech recognition!\n")
            self.text_log.see("end")
            return False
        else:
            self.apikey = api_key
        return True

    def start_asr(self):
        if not self._check_has_input_api():
            self.text_log.insert("end", f"{self.time_str}: Please input API Key for speech recognition!\n")
            self.text_log.see("end")
            return
        else:
            # 如果没有保存过，则保存到本地文件
            if not os.path.exists(get_resource_path("api_key.txt")):
                with open(get_resource_path("api_key.txt"), 'w') as f:
                    f.write(self.apikey)
            self.text_log.insert("end", f"{self.time_str}: API Key saved to api_key.txt, and will be auto-loaded on next start.\n")
            self.text_log.see("end")
        self.btn_asr_start['state'] = 'disabled'
        self.btn_asr_stop['state'] = 'normal'
        self.is_speech_recognizing = True

        if not self.is_capturing:
            self._init_auto_save_dir()

        if self.is_capturing:
            self.btn_all_start['state'] = 'disabled'
            self.btn_all_stop['state'] = 'normal'

        log_filename = os.path.join(self.save_path, f"asr_log_{time.strftime('%Y%m%d-%H%M%S', time.localtime())}.txt")
        
        self.asr_proc_mic = multiprocessing.Process(target=run_asr_process, args=(log_filename, self.asr_queue, self.apikey, self.stereo_mix_index, "mic"))
        self.asr_proc_stereo = multiprocessing.Process(target=run_asr_process, args=(log_filename, self.asr_queue, self.apikey, self.stereo_mix_index, "stereo mix"))
        self.asr_proc_mic.daemon = True
        self.asr_proc_stereo.daemon = True

        self.asr_proc_mic.start()
        self.asr_proc_stereo.start()
        
        self.is_asr_queue_checking = True
        self.poll_asr_queues()
        
    def stop_asr(self):
        self.is_speech_recognizing = False
        self.btn_asr_start['state'] = 'normal'
        self.btn_asr_stop['state'] = 'disabled'

        if not self.is_capturing:
            self.btn_all_start['state'] = 'normal'
            self.btn_all_stop['state'] = 'disabled'
        
        # 关闭进程
        if hasattr(self, 'asr_proc_mic') and self.asr_proc_mic.is_alive():
            self.asr_proc_mic.terminate()
            self.asr_proc_mic.join()
        if hasattr(self, 'asr_proc_stereo') and self.asr_proc_stereo.is_alive():
            self.asr_proc_stereo.terminate()
            self.asr_proc_stereo.join()
        
        self.text_asr.insert("end", f"{self.time_str}: Speech recognition stopped.\n")
        self.text_asr.see("end")

    def poll_asr_queues(self):
        if not self.is_asr_queue_checking:
            return
        while not self.asr_queue.empty():
            msg = self.asr_queue.get()
            self.text_asr.insert("end", msg)
            self.text_asr.see("end")
        self.root.after(200, self.poll_asr_queues)  # 200ms轮询一次

    def show_state_window(self):
        if self.is_show_state_window_var.get():
            self.state_window.deiconify()
        else:
            self.state_window.withdraw()

    def __init_state_window(self):
        self.state_window = tk.Toplevel()
        self.state_window.attributes("-topmost", True)  # 窗口置顶
        self.state_window.overrideredirect(True)         # 隐藏窗口的标题栏
        self.state_window.attributes("-alpha", 0.3)      # 窗口透明度10%
        self.state_window.geometry("{0}x{1}+{2}+{3}".format(40, 40, self.win_width - 200, 70))

        self.label_capture_state = tk.Label(self.state_window, text="S-C", bg="orange", font=("Arial", 8))
        self.label_capture_state.place(relx=0.5, rely=0, relwidth=0.5, relheight=0.5)

        self.label_monitoring_state = tk.Label(self.state_window, text="S-M", bg="orange", font=("Arial", 8))
        self.label_monitoring_state.place(relx=0, rely=0, relwidth=0.5, relheight=0.5)
        
        self.label_mic_listening_state = tk.Label(self.state_window, text="Mic", bg="orange", font=("Arial", 8))
        self.label_mic_listening_state.place(relx=0, rely=0.5, relwidth=0.5, relheight=0.5)

        self.label_stereo_mix_listening_state = tk.Label(self.state_window, text="Mix", bg="orange", font=("Arial", 8))
        self.label_stereo_mix_listening_state.place(relx=0.5, rely=0.5, relwidth=0.5, relheight=0.5)

        self.state_window.bind("<Button-1>", self._state_window_on_start)
        self.state_window.bind("<B1-Motion>", self._state_window_on_drag)
        self.state_window.bind("<ButtonRelease-1>", self._state_window_on_stop)
    
    def _state_window_on_start(self, event):
        self.mouse_x, self.mouse_y = event.x, event.y

    def _state_window_on_drag(self, event):
        x, y = event.x, event.y
        self.state_window.geometry(f"{40}x{40}+{self.state_window.winfo_x() + x - self.mouse_x}+{self.state_window.winfo_y() + y - self.mouse_y}")

    def _state_window_on_stop(self, event):
        self.mouse_x, self.mouse_y = 0, 0

    def update_monitoring_state(self):
        self.label_monitoring_state["bg"] = "red" if self.label_monitoring_state["bg"] == "orange" else "orange"

    def update_capture_state(self, func='on'):
        if func == 'on':
            self.label_capture_state["bg"] = "red"
        elif func == 'off':
            self.label_capture_state["bg"] = "orange"
        
    def get_capture_window(self):
        self.root.iconify() # 最小化窗口
        cws = Capture_window_select(self.capture_window)
        self.root.deiconify() # 还原窗口
        self.capture_window = cws.get_capture_window_coor()
        # 显示截图区域信息到文本框, 包含时间
        self.text_info.insert("end", f"{self.time_str}:\n   Capture window:{self.capture_window}\n")
        self.label_capture_window['text'] = f"({self.capture_window[0]},{self.capture_window[1]})->({self.capture_window[2]},{self.capture_window[3]})"
        if self.capture_window is not None:
            self.btn_start['state'] = 'normal'

    def capture(self):
        self.update_monitoring_state()
        self.update_capture_state('off')

        im2 = ImageGrab.grab(bbox=self.capture_window, include_layered_windows=False, all_screens=True)

        diff = ImageChops.difference(self.im, im2)
        diff = sum(ImageStat.Stat(diff).mean)
        # diff = np.mean((np.array(self.im) - np.array(im2))**2) / (self.im_l * self.im_w)
        if  diff > self.sensitivity:
            if self.is_capturing:
                import os
                img_path = os.path.join(self.save_path, f'{self.time_str}.png')
                im2.save(img_path)
                self.text_info.insert("end", f"\n{self.time_str}:\n   diff={diff:.1f}, PPT slide change detected!\n")
                self.text_info.see("end")
                self.update_capture_state('on')
        else:
            if self.is_capturing: self.text_info.insert("end", f"E={diff:.1f};")
        
        self.im = im2

        if not self.is_capturing:
            return
        
        self.root.after(int(self.capture_interval * 1000), self.capture)

    def start_capture(self):
        self.is_capturing = True
        self.capture_interval = float(self.ety_capture_interval.get())
        self.sensitivity = self.scb_sensitivity.get()
        self.text_info.insert("end", f"\n{self.time_str}:\n   Capture started!\n")
        self.text_info.insert("end", f"   Check interval={self.capture_interval}s, sensitivity={self.sensitivity}\n")
        self.btn_start['state'] = 'disabled'
        self.btn_stop['state'] = 'normal'

        if not self.is_speech_recognizing:
            self._init_auto_save_dir()

        self.im = ImageGrab.grab(bbox=self.capture_window, include_layered_windows=False, all_screens=True)
        self.im.save(rf'{self.save_path}\{self.time_str}.png')
        self.im_l, self.im_w = self.im.size
        self.im_l, self.im_w = self.im_l/1000, self.im_w/1000

        if self.is_speech_recognizing:
            self.btn_all_start['state'] = 'disabled'
            self.btn_all_stop['state'] = 'normal'

        self.capture()

    def stop_capture(self):
        self.text_info.insert("end", f"\n{self.time_str}:\n   Capture stopped!\n")
        self.btn_start['state'] = 'normal'
        self.btn_stop['state'] = 'disabled'
        self.is_capturing = False

        if not self.is_speech_recognizing:
            self.btn_all_start['state'] = 'normal'
            self.btn_all_stop['state'] = 'disabled'

        self.label_monitoring_state["bg"] = "orange"
        self.label_capture_state["bg"] = "orange"

    def sys_out(self):
        # 终止语音识别子进程
        try:
            if hasattr(self, "asr_proc_mic") and self.asr_proc_mic.is_alive():
                self.asr_proc_mic.terminate()
            if hasattr(self, "asr_proc_stereo") and self.asr_proc_stereo.is_alive():
                self.asr_proc_stereo.terminate()
        except Exception as e:
            print(f"Terminate process error: {e}")

        self.is_capturing = False
        self.is_speech_recognizing = False
        self.is_asr_queue_checking = False

        self.root.destroy()
        self.root.quit()

    def on_close(self):
        # 终止语音识别子进程
        try:
            if hasattr(self, "asr_proc_mic") and self.asr_proc_mic.is_alive():
                self.asr_proc_mic.terminate()
            if hasattr(self, "asr_proc_stereo") and self.asr_proc_stereo.is_alive():
                self.asr_proc_stereo.terminate()
        except Exception as e:
            print(f"Terminate process error: {e}")
        self.root.destroy()

    def open_save_path(self):
        if self.save_path and os.path.exists(self.save_path):
            os.startfile(self.save_path)
        else:
            self.text_log.insert("end", f"{self.time_str}: No valid save path!\n")
            self.text_log.see("end")

    def show_help(self):
        # open a new window, containing a text box with help information
        help_window = tk.Toplevel(self.root)
        help_window.title("Help")
        help_text = tk.Text(help_window, wrap="word")
        help_text.insert("end", "This is the help information.")
        help_text.pack(expand=True, fill="both")

    @property
    def time_str(self):
        return time.strftime("%Y%m%d-%H%M%S", time.localtime())

if __name__ == "__main__":
    ScreenCapture()