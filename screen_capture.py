# Repositories url: https://github.com/ChenChenGith/Video_PPT_capture

# version: 0.1.0
# license: MIT

from PIL import ImageGrab
import time
import numpy as np
import tkinter as tk
from tkinter import filedialog
import sys, os

class Capture_window_select(object):
    def __init__(self, capture_window=None):
        self.window = tk.Tk()
        self.width = self.window.winfo_screenwidth()
        self.height = self.window.winfo_screenheight()

        self.window.overrideredirect(True)         # 隐藏窗口的标题栏
        self.window.attributes("-alpha", 0.5)      # 窗口透明度10%
        self.window.geometry("{0}x{1}+0+0".format(self.width, self.height))

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

        self.canvas.create_text(self.width - 500, self.height - 500, text=f"Esc", fill="red", tags="info", font=("Arial", 16))

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
    
    def selection_start(self, event):
        self.canvas.delete("rect", "text")
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2, tags="rect", dash=(4, 4))
        self.canvas.create_text(self.start_x + 35, self.start_y + 10, text=f"({self.start_x}, {self.start_y})", fill="red", tags="text")
    
    def selection_end(self, event):
        self.end_x = event.x
        self.end_y = event.y
        self.capture_window = (self.start_x, self.start_y, self.end_x, self.end_y)
        self.canvas.create_text(self.end_x - 90, self.end_y - 25, text=f"({self.end_x}, {self.end_y})({self.end_x-self.start_x}X{self.end_y-self.start_y})", fill="red", tags="text")
        self.canvas.create_text(self.end_x - 100, self.end_y - 10, text="Press Enter to confirm selection", fill="red", tags="text")

    def change_selection(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
    
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

class ScreenCapture(object):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PPT in Video Capture Tool. CC:ChenChenGith@github")
        win_width, win_height = int(min(self.root.winfo_screenwidth()/4, 500)), int(min(self.root.winfo_screenheight(), 500))
        self.root.geometry("{0}x{1}+0+0".format(win_width, win_height))
        
        self.root.iconbitmap(get_resource_path("./ycy.ico"))

        # 文本信息框
        self.text_info = tk.Text(self.root)
        self.text_info.place(relx=0.05, rely=0.05, relwidth=0.63, relheight=0.9) 
        # 指定截图检查间隔时间（秒）
        tk.Label(self.root, text="Check Interval (s)").place(relx=0.70, rely=0.05, relwidth=0.28, relheight=0.04)
        self.ety_capture_interval = tk.Entry(self.root, justify="center")
        self.ety_capture_interval.insert(0, "5")
        self.ety_capture_interval.place(relx=0.78, rely=0.09, relwidth=0.1, relheight=0.05)
        # 敏感度选择滑动条
        self.scb_sensitivity = tk.Scale(self.root, from_=0, to=20, orient="horizontal", label="Sensitivity (0=High)", resolution=1, length=50)
        self.scb_sensitivity.place(relx=0.70, rely=0.14, relwidth=0.28, relheight=0.13)
        self.scb_sensitivity.set(2)
        # 指定截图区域按钮
        self.btn_window_config = tk.Button(self.root, text="Capt. Win. Selection", command=self.get_capture_window)
        self.btn_window_config.place(relx=0.70, rely=0.28, relwidth=0.28, relheight=0.08)
        # 当前截图区域
        tk.Label(self.root, text="Capt. Win. Info:", fg='gray').place(relx=0.70, rely=0.36, relwidth=0.28, relheight=0.05)
        self.label_capture_window = tk.Label(self.root, text="None", fg="gray")
        self.label_capture_window.place(relx=0.70, rely=0.41, relwidth=0.28, relheight=0.08)

        # 指定文件保存路径按钮
        self.btn_save_path = tk.Button(self.root, text="Img. Path Selection", command=self.determine_save_path)
        self.btn_save_path.place(relx=0.70, rely=0.49, relwidth=0.28, relheight=0.1)
        # # 当前文件保存路径
        tk.Label(self.root, text="Img. Save Path", fg='gray').place(relx=0.72, rely=0.59, relwidth=0.28, relheight=0.05)
        self.label_save_path = tk.Text(self.root, fg="gray", bd=0)
        self.label_save_path.insert("end", "None")
        self.label_save_path.place(relx=0.70, rely=0.64, relwidth=0.28, relheight=0.1)
        # 开始截图按钮
        self.btn_start = tk.Button(self.root, text="Start", command=self.start_capture, state="disabled")
        self.btn_start.place(relx=0.70, rely=0.76, relwidth=0.12, relheight=0.1)
        # 停止截图按钮
        self.btn_stop = tk.Button(self.root, text="Stop", command=self.stop_capture, state="disabled")
        self.btn_stop.place(relx=0.85, rely=0.76, relwidth=0.12, relheight=0.1)
        # 退出按钮
        self.btn_sys_out = tk.Button(self.root, text="Exit", command=self.sys_out)
        self.btn_sys_out.place(relx=0.70, rely=0.88, relwidth=0.28, relheight=0.07)

        
        self.sensitivity = None
        self.is_capturing = False
        self.capture_window = None
        self.save_path = None
        self.im = None

        self.mouse_x, self.mouse_y = 0, 0

        self.__init_state_window()

        self.root.mainloop()

    def __init_state_window(self):
        self.state_window = tk.Toplevel()
        self.state_window.attributes("-topmost", True)  # 窗口置顶
        self.state_window.overrideredirect(True)         # 隐藏窗口的标题栏
        self.state_window.attributes("-alpha", 0.3)      # 窗口透明度10%
        self.state_window.geometry("{0}x{1}+{2}+{3}".format(40, 20, self.state_window.winfo_screenwidth()-80, self.state_window.winfo_screenheight() - 80))

        self.label_capture_state = tk.Label(self.state_window, text="C", bg="orange")
        self.label_capture_state.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)

        self.label_monitoring_state = tk.Label(self.state_window, text="M", bg="orange")
        self.label_monitoring_state.place(relx=0, rely=0, relwidth=0.5, relheight=1)

        self.state_window.bind("<Button-1>", self._state_window_on_start)
        self.state_window.bind("<B1-Motion>", self._state_window_on_drag)
        self.state_window.bind("<ButtonRelease-1>", self._state_window_on_stop)
    
    def _state_window_on_start(self, event):
        self.mouse_x, self.mouse_y = event.x, event.y

    def _state_window_on_drag(self, event):
        x, y = event.x, event.y
        self.state_window.geometry(f"{40}x{20}+{self.state_window.winfo_x() + x - self.mouse_x}+{self.state_window.winfo_y() + y - self.mouse_y}")

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
        self.label_capture_window['text'] = f"({self.capture_window[0]},{self.capture_window[1]})\n({self.capture_window[2]},{self.capture_window[3]})"
        if self.capture_window != None and self.save_path != None:
            self.btn_start['state'] = 'normal'

    def capture(self):
        self.update_monitoring_state()
        self.update_capture_state('off')

        im2 = ImageGrab.grab(bbox=self.capture_window, include_layered_windows=False, all_screens=True)

        diff = np.mean((np.array(self.im) - np.array(im2))**2) / (self.im_l * self.im_w)
        if  diff> self.sensitivity:
            if self.is_capturing: 
                im2.save(rf'{self.save_path}\{self.time_str}.png')
                self.text_info.insert("end", f"\n{self.time_str}:\n   diff={diff:.2f}, PPT slide change detected!\n")
                self.text_info.see("end")
                self.update_capture_state('on')
        else:
            if self.is_capturing: self.text_info.insert("end", ".")
        
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

        self.im = ImageGrab.grab(bbox=self.capture_window, include_layered_windows=False, all_screens=True)
        self.im.save(rf'{self.save_path}\{self.time_str}.png')
        self.im_l, self.im_w = self.im.size
        self.im_l, self.im_w = self.im_l/1000, self.im_w/1000

        self.capture()

    def stop_capture(self):
        self.text_info.insert("end", f"\n{self.time_str}:\n   Capture stopped!\n")
        self.btn_start['state'] = 'normal'
        self.btn_stop['state'] = 'disabled'
        self.is_capturing = False

        self.label_monitoring_state["bg"] = "orange"
        self.label_capture_state["bg"] = "orange"

    def sys_out(self):
        self.is_capturing = False
        self.root.destroy()
        self.root.quit()
        
    def determine_save_path(self):
        self.save_path = filedialog.askdirectory() # 打开文件夹对话框
        self.text_info.insert("end", f"{self.time_str}:\n   Image save path: {self.save_path}\n")
        self.label_save_path.delete("1.0", "end")
        self.label_save_path.insert("end", self.save_path)
        if self.capture_window != None and self.save_path != None:
            self.btn_start['state'] = 'normal'
        

    @property
    def time_str(self):
        return time.strftime("%Y%m%d-%H%M%S", time.localtime())

if __name__ == "__main__":
    ScreenCapture()