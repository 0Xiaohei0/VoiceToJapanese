import time
import customtkinter
import subLocal as SUB
from threading import Thread
import sounddevice as sd
import numpy as np

audio_level = 0.3


class App(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.geometry("1920x1080+0+0")
        self.title("app")
        self.resizable(False, False)
        self.overrideredirect(1)
        self.attributes("-topmost", True)
        self.wm_attributes('-transparentcolor', 'black')
        self.configure(fg_color='black')
        self.label = customtkinter.CTkLabel(
            master=self, text='default text', fg_color='black', text_color="white", font=("Arial", 45), wraplength=1500, anchor='w')
        self.label.place(relx=0.2, rely=0.8, anchor='w')


class Config(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.geometry("300x600")
        self.title("Subtitler config")
        self.resizable(False, False)
        self.label = customtkinter.CTkLabel(
            master=self, text='Subtitle position')
        self.label.pack(padx=10, pady=10)
        self.sub_pos_x = 0.2
        self.sub_pos_y = 0.8

        xslider = customtkinter.CTkSlider(
            master=self, from_=0, to=100, command=self.slider_event_x)
        xslider.pack(padx=10, pady=10)
        yslider = customtkinter.CTkSlider(
            master=self, from_=0, to=100,  command=self.slider_event_y)
        yslider.pack(padx=10, pady=10)

        self.default_input_anguage = "Japanese"
        self.default_output_anguage = "English"
        self.input_anguage = ["English", "Japanese", "Chinese"]

        label_Input = customtkinter.CTkLabel(
            master=self, text='Input Language: ')
        label_Input.pack(padx=20, pady=10)
        inputbox_var = customtkinter.StringVar(
            value=self.default_input_anguage)
        combobox = customtkinter.CTkComboBox(master=self,
                                             values=self.input_anguage,
                                             command=self.input_dropdown_callbakck,
                                             variable=inputbox_var)
        combobox.pack(padx=20, pady=0)

        label_Input = customtkinter.CTkLabel(
            master=self, text='Output Language: ')
        label_Input.pack(padx=20, pady=10)
        outputbox_var = customtkinter.StringVar(
            value=self.default_output_anguage)
        combobox = customtkinter.CTkComboBox(master=self,
                                             values=self.input_anguage,
                                             command=self.output_dropdown_callbakck,
                                             variable=outputbox_var)
        combobox.pack(padx=20, pady=10)

        label_mic = customtkinter.CTkLabel(
            master=self, text='Mic activity: ')
        label_mic.pack(padx=20, pady=10)
        self.progressbar = customtkinter.CTkProgressBar(master=self, width=100)
        self.progressbar.pack(padx=20, pady=0)
        thread = Thread(target=self.update_mic_meter_loop)
        thread.start()

    def slider_event_x(self, value):
        self.sub_pos_x = value/100
        move_text(self.sub_pos_x, self.sub_pos_y)

    def slider_event_y(self, value):
        self.sub_pos_y = value/100
        move_text(self.sub_pos_x, self.sub_pos_y)

    def update_mic_meter_loop(self):
        while True:
            self.update_mic_meter()

    def update_mic_meter(self):
        global audio_level
        self.progressbar.set(audio_level)
        time.sleep(0.01)

    def input_dropdown_callbakck(self, choice):
        SUB.change_input_language(choice)

    def output_dropdown_callbakck(self, choice):
        SUB.change_output_language(choice)


app = App()
config = Config()


def update_text(text):
    app.label.configure(text=text)


def move_text(x, y):
    app.label.place(relx=x, rely=y, anchor='w')


SUB.text_change_eventhandlers.append(update_text)


def start_recording_loop():
    while (True):
        SUB.start_translator()


thread = Thread(target=SUB.start_translator)
thread.start()


def print_sound(indata, outdata, frames, time, status):
    global audio_level
    audio_level = np.linalg.norm(indata)/10


def listen_to_mic():
    with sd.Stream(callback=print_sound):
        sd.sleep(10000000)


thread = Thread(target=listen_to_mic)
thread.start()

config.mainloop()
