from threading import Thread
import customtkinter
import keyboard
import pyaudio
import STTSLocal as STTS
from threading import Event
from enum import Enum
import sounddevice as sd
import speech_recognition as sr
import numpy as np
import time
import subLocal as SUB
import translator
import chatbot


class Pages(Enum):
    AUDIO_INPUT = 0
    TEXT_INPUT = 1
    SETTINGS = 2
    SUBTITLE = 3
    CHAT = 4


current_page = Pages.AUDIO_INPUT
pageChange_eventhandlers = []
audio_level = 0.3

mic_meters = []


class SidebarFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        global current_page
        super().__init__(master, **kwargs)

        Audio_input_Button = customtkinter.CTkButton(master=self,
                                                     width=120,
                                                     height=32,
                                                     border_width=0,
                                                     corner_radius=0,
                                                     text="Audio input",
                                                     command=lambda: self.change_page(
                                                         Pages.AUDIO_INPUT),
                                                     fg_color='grey'
                                                     )
        Audio_input_Button.pack(anchor="s")
        # add widgets onto the frame...
        text_input_button = customtkinter.CTkButton(master=self,
                                                    width=120,
                                                    height=32,
                                                    border_width=0,
                                                    corner_radius=0,
                                                    text="Text input",
                                                    command=lambda: self.change_page(
                                                        Pages.TEXT_INPUT),
                                                    fg_color='grey'
                                                    )
        text_input_button.pack(anchor="s")

        subtitles_button = customtkinter.CTkButton(master=self,
                                                   width=120,
                                                   height=32,
                                                   border_width=0,
                                                   corner_radius=0,
                                                   text="Subtitles",
                                                   command=lambda: self.change_page(
                                                        Pages.SUBTITLE),
                                                   fg_color='grey'
                                                   )
        subtitles_button.pack(anchor="s")

        chat_button = customtkinter.CTkButton(master=self,
                                              width=120,
                                              height=32,
                                              border_width=0,
                                              corner_radius=0,
                                              text="Chat",
                                              command=lambda: self.change_page(
                                                  Pages.CHAT),
                                              fg_color='grey'
                                              )
        chat_button.pack(anchor="s")

        button = customtkinter.CTkButton(master=self,
                                         width=120,
                                         height=32,
                                         border_width=0,
                                         corner_radius=0,
                                         text="Settings",
                                         command=lambda: self.change_page(
                                             Pages.SETTINGS),
                                         fg_color='grey'
                                         )
        button.pack(anchor="s")

    def change_page(self, page):
        global current_page
        current_page = page

        global pageChange_eventhandlers
        for eventhandler in pageChange_eventhandlers:
            eventhandler()


class ConsoleFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.isRecording = False
        self.stop_recording_event = Event()
        self.thread = Thread(target=STTS.start_record_auto,
                             args=(self.stop_recording_event,))
        # add widgets onto the frame...
        self.textbox = customtkinter.CTkTextbox(self, width=400, height=400)
        self.textbox.grid(row=0, column=0, rowspan=2, columnspan=3)
        # configure textbox to be read-only
        self.textbox.configure(state="disabled")
        STTS.logging_eventhandlers.append(self.log_message_on_console)

        self.recordButton = customtkinter.CTkButton(master=self,
                                                    width=120,
                                                    height=32,
                                                    border_width=0,
                                                    corner_radius=8,
                                                    text="Start Recording",
                                                    command=self.recordButton_callback,
                                                    fg_color='grey'
                                                    )
        self.recordButton.grid(row=3, column=0, pady=10)

        self.playOriginalButton = customtkinter.CTkButton(master=self,
                                                          width=120,
                                                          height=32,
                                                          border_width=0,
                                                          corner_radius=8,
                                                          text="Play original",
                                                          command=self.play_original_callback,
                                                          fg_color='grey'
                                                          )
        self.playOriginalButton.grid(row=3, column=1, pady=10)

        self.clearConsoleButton = customtkinter.CTkButton(master=self,
                                                          width=32,
                                                          height=32,
                                                          border_width=0,
                                                          corner_radius=8,
                                                          text="X",
                                                          command=self.clear_console,
                                                          fg_color='grey'
                                                          )
        self.clearConsoleButton.grid(row=3, column=2, padx=10, pady=10)

    def clear_console(self):
        self.textbox.configure(state="normal")
        self.textbox.delete('1.0', customtkinter.END)
        self.textbox.configure(state="disabled")

    def recordButton_callback(self):
        if (self.isRecording):
            self.recordButton.configure(
                text="Start Recording", fg_color='grey')
            self.isRecording = False
            STTS.stop_record_auto()
        else:
            self.recordButton.configure(
                text="Stop Recording", fg_color='#fc7b5b')
            self.isRecording = True
            STTS.start_record_auto()
        self.recordButton.grid(row=3, column=0, pady=10)

    def play_original_callback(self):
        thread = Thread(target=STTS.playOriginal())
        thread.start()

    def log_message_on_console(self, message_text):
        # insert at line 0 character 0
        self.textbox.configure(state="normal")
        self.textbox.insert(customtkinter.INSERT, message_text+'\n')
        self.textbox.configure(state="disabled")


class ChatFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.isRecording = False
        self.thread = Thread(target=STTS.start_record_auto)
        # add widgets onto the frame...
        self.textbox = customtkinter.CTkTextbox(self, width=400, height=400)
        self.textbox.grid(row=0, column=0, rowspan=4, columnspan=4)
        # configure textbox to be read-only
        self.textbox.configure(state="disabled")
        chatbot.logging_eventhandlers.append(self.log_message_on_console)

        self.user_input_var = customtkinter.StringVar(self, '')
        self.voicevox_api_key_input = customtkinter.CTkEntry(
            master=self, textvariable=self.user_input_var, width=200)
        self.voicevox_api_key_input.grid(
            row=4, column=0, padx=10, pady=10, sticky='W', columnspan=2)
        self.send_button = customtkinter.CTkButton(master=self,
                                                   width=32,
                                                   height=32,
                                                   border_width=0,
                                                   corner_radius=8,
                                                   text="send",
                                                   command=self.send_user_input,
                                                   fg_color='grey'
                                                   )
        self.send_button.grid(row=4, column=2, pady=10)
        self.recordButton = customtkinter.CTkButton(master=self,
                                                    width=120,
                                                    height=32,
                                                    border_width=0,
                                                    corner_radius=8,
                                                    text="Start Recording",
                                                    command=self.recordButton_callback,
                                                    fg_color='grey'
                                                    )
        self.recordButton.grid(row=4, column=3, pady=10)

        # self.playOriginalButton = customtkinter.CTkButton(master=self,
        #                                                   width=120,
        #                                                   height=32,
        #                                                   border_width=0,
        #                                                   corner_radius=8,
        #                                                   text="Play original",
        #                                                   command=self.play_original_callback,
        #                                                   fg_color='grey'
        #                                                   )
        # self.playOriginalButton.grid(row=3, column=1, pady=10)

        # self.clearConsoleButton = customtkinter.CTkButton(master=self,
        #                                                   width=32,
        #                                                   height=32,
        #                                                   border_width=0,
        #                                                   corner_radius=8,
        #                                                   text="X",
        #                                                   command=self.clear_console,
        #                                                   fg_color='grey'
        #                                                   )
        # self.clearConsoleButton.grid(row=3, column=2, padx=10, pady=10)

    # def clear_console(self):
    #     self.textbox.configure(state="normal")
    #     self.textbox.delete('1.0', customtkinter.END)
    #     self.textbox.configure(state="disabled")

    def recordButton_callback(self):
        if (self.isRecording):
            self.recordButton.configure(
                text="Start Recording", fg_color='grey')
            self.isRecording = False
            STTS.stop_record_auto()
        else:
            self.recordButton.configure(
                text="Stop Recording", fg_color='#fc7b5b')
            self.isRecording = True
            STTS.start_record_auto_chat()

    # def play_original_callback(self):
    #     thread = Thread(target=STTS.playOriginal())
    #     thread.start()
    def send_user_input(self):
        text = self.user_input_var.get()
        self.user_input_var.set('')
        thread = Thread(target=chatbot.send_user_input, args=[text,])
        thread.start()

    def log_message_on_console(self, message_text):
        # insert at line 0 character 0
        self.textbox.configure(state="normal")
        self.textbox.insert(customtkinter.INSERT, message_text+'\n')
        self.textbox.configure(state="disabled")


class TextBoxFrame(customtkinter.CTkFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.default_message = "Hello, how are you doing?"
        self.text_input = customtkinter.CTkTextbox(self, width=400, height=400)
        self.text_input.grid(row=0, column=0, rowspan=2, columnspan=2)
        self.text_input.insert(customtkinter.INSERT, self.default_message+'\n')
        self.synthesizeButton = customtkinter.CTkButton(master=self,
                                                        width=120,
                                                        height=32,
                                                        border_width=0,
                                                        corner_radius=8,
                                                        text="Synthesize",
                                                        command=self.synthesizeButton_callback,
                                                        fg_color='grey'
                                                        )
        self.synthesizeButton.grid(
            row=3, column=0, padx=10, pady=10, sticky="w")

    def synthesizeButton_callback(self):
        STTS.start_TTS_pipeline(self.text_input.get("1.0", customtkinter.END))


class AudiodeviceSelection(customtkinter.CTkFrame):
    # set_command is called with updated device_id
    # get_command should return the device_id for the mic meter
    # device_type can be None, input or output for device filtering
    def __init__(self, set_command, get_command, master, device_type=None, show_device_selection=True, show_driver_selection=True, show_mic_meter=True, **kwargs):
        super().__init__(master, **kwargs)
        # Mic meter
        self.set_command = set_command
        self.get_command = get_command
        self.audio_level = 0.3
        self.device_type = device_type
        # driver selection
        if (show_driver_selection):
            audio_driver_label = customtkinter.CTkLabel(
                master=self, text='Audio driver: ')
            audio_driver_label.grid(
                row=0, column=0, padx=10, pady=10, sticky='W')
            self.audio_drivers = self.get_audio_drivers()
            self.audio_driver_names = list(
                map(lambda driver: driver['name'], self.audio_drivers))
            self.audio_input_combobox_var = customtkinter.StringVar(
                value=self.audio_driver_names[0])
            self.audio_input_combobox = customtkinter.CTkComboBox(master=self,
                                                                  values=self.audio_driver_names,
                                                                  command=self.audio_driver_dropdown_callback,
                                                                  variable=self.audio_input_combobox_var)
            self.audio_input_combobox.grid(
                row=0, column=1, padx=10, pady=10, sticky='W')

        if (show_device_selection):
            # device selection
            audio_input_label = customtkinter.CTkLabel(
                master=self, text=f'{device_type} device: ')
            audio_input_label.grid(
                row=1, column=0, padx=10, pady=10, sticky='W')
            self.audio_devices = self.get_audio_devices()
            self.filtered_devices = self.audio_devices
            if (self.device_type == 'input'):
                self.filtered_devices = list(filter(
                    lambda device: device['max_input_channels'] > 0, self.audio_devices))
            elif (self.device_type == 'output'):
                self.filtered_devices = list(filter(
                    lambda device: device['max_output_channels'] > 0, self.audio_devices))
            self.input_audio_device_names = list(
                map(lambda device: device['name'], self.filtered_devices))
            self.input_audio_device_names.insert(0, 'Default')
            self.audio_input_combobox_var = customtkinter.StringVar(
                value='Default')
            self.audio_input_combobox = customtkinter.CTkComboBox(master=self,
                                                                  values=self.input_audio_device_names,
                                                                  command=self.audio_input_dropdown_callbakck,
                                                                  variable=self.audio_input_combobox_var)
            self.audio_input_combobox.grid(
                row=1, column=1, padx=10, pady=10, sticky='W')

        if (self.device_type == 'input' and show_mic_meter):
            label_mic = customtkinter.CTkLabel(
                master=self, text='Mic activity: ')
            label_mic.grid(row=2, column=0, padx=10, pady=10, sticky='W')
            self.progressbar = customtkinter.CTkProgressBar(
                master=self, width=100)
            self.progressbar.grid(
                row=3, column=0, padx=10, pady=10, sticky='W')
            thread = Thread(target=self.update_mic_meter_loop)
            thread.start()
            self.listen_to_mic_thread = Thread(target=self.listen_to_mic)
            self.listen_to_mic_thread.start()
            global mic_meters
            mic_meters.append(self)

    def update_mic_meter_loop(self):
        while True:
            self.update_mic_meter()

    def update_mic_meter(self):
        self.progressbar.set(self.audio_level)
        time.sleep(0.01)

    def listen_to_mic(self):
        self._subtitle_mic_stream = sd.InputStream(
            callback=self.update_sound, device=self.get_command())
        with self._subtitle_mic_stream:
            sd.sleep(10000000)

    def audio_input_dropdown_callbakck(self, choice):
        device_id = None
        if (choice == 'Default'):
            device_id = None
        else:
            print(choice)
            device = next(
                device for device in self.filtered_devices if device['name'] == choice)
            device_id = device['index']
            print(device)
        print(f'Setting {self.device_type} audio device id to: {device_id}')
        self.set_command(device_id)
        if (self.device_type == 'input'):
            print(f"restarted micmeter with device id: {device_id}")
            self.restart_mic_meter()

    def restart_mic_meter(self):
        global mic_meters
        for mic in mic_meters:
            print(mic.listen_to_mic_thread)
            mic._subtitle_mic_stream.stop()
            mic.listen_to_mic_thread.join()
            mic.listen_to_mic_thread = Thread(target=self.listen_to_mic)
            mic.listen_to_mic_thread.start()

    def audio_driver_dropdown_callback(self, choice):
        print(choice)
        driver_idx = 0
        for idx, driver in enumerate(self.audio_drivers):
            if driver['name'] == choice:
                driver_idx = idx
        print(f'Selected driver with idx: {driver_idx}')
        self.audio_devices = self.get_audio_devices(hostapi=driver_idx)
        self.filtered_devices = self.audio_devices
        if (self.device_type == 'input'):
            self.filtered_devices = list(filter(
                lambda device: device['max_input_channels'] > 0, self.audio_devices))
        elif (self.device_type == 'output'):
            self.filtered_devices = list(filter(
                lambda device: device['max_output_channels'] > 0, self.audio_devices))
        self.input_audio_device_names = list(
            map(lambda device: device['name'], self.filtered_devices))
        self.input_audio_device_names.insert(0, 'Default')
        self.audio_input_combobox_var = customtkinter.StringVar(
            value='Default')
        self.audio_input_combobox.configure(values=self.input_audio_device_names,
                                            variable=self.audio_input_combobox_var)
        print(self.input_audio_device_names)
        device_id = None
        print(f'Setting {self.device_type} audio device id to: {device_id}')
        self.set_command(device_id)
        if (self.device_type == 'input'):
            print(f"restarted micmeter with device id: {device_id}")
            self.restart_mic_meter()

    def get_audio_drivers(self):
        hostapis = sd.query_hostapis()
        # print(hostapis)
        return hostapis

    def get_audio_devices(self, hostapi=0):
        devices = list(filter(
            lambda device: device['hostapi'] == hostapi, sd.query_devices()))
        # print(devices)
        return devices

    def update_sound(self, indata, outdata, frames, time):
        self.audio_level = np.linalg.norm(indata)/10
        # print("|" * int(volume_norm))


class SubtitlesFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.subtitle_overlay = None
        self.label = customtkinter.CTkLabel(
            master=self, text='Subtitle position')
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky='W')
        self.sub_pos_x = 0.2
        self.sub_pos_y = 0.8

        xslider = customtkinter.CTkSlider(
            master=self, from_=0, to=100, command=self.slider_event_x)
        xslider.grid(row=0, column=1, padx=10, pady=10, sticky='W')
        yslider = customtkinter.CTkSlider(
            master=self, from_=0, to=100,  command=self.slider_event_y)
        yslider.grid(row=0, column=2, padx=10, pady=10, sticky='W')

        self.phrase_max_length_var = customtkinter.IntVar(
            value=5)
        self.phrase_max_length_label = customtkinter.CTkLabel(
            master=self, text=f'Phrase max length: {self.phrase_max_length_var.get()}')
        self.phrase_max_length_label.grid(
            row=3, column=0, padx=10, pady=10, sticky='W')
        self.phrase_max_length_slider = customtkinter.CTkSlider(
            master=self, from_=3, to=30, command=self.update_phrase_max_length, variable=self.phrase_max_length_var)
        self.phrase_max_length_slider.grid(
            row=3, column=1, padx=10, pady=10, sticky='W')

        self.audio_device_selection = AudiodeviceSelection(
            master=self, set_command=self.device_index_update_callback, get_command=self.device_index_get_callback, device_type='input')
        self.audio_device_selection.grid(
            row=4, column=0, padx=10, pady=10, sticky='W', rowspan=1, columnspan=2)

        self.toggle_overlay_button = customtkinter.CTkButton(
            self, text="start overlay", command=self.toggle_subtitle_button_callback)
        self.toggle_overlay_button.grid(
            row=5, column=0, padx=10, pady=10, sticky='W')

        self.hide_border_var = customtkinter.BooleanVar(self, True)
        show_border_checkbox = customtkinter.CTkCheckBox(master=self, text="Hide border on overlay", command=self.set_show_border,
                                                         variable=self.hide_border_var, onvalue=True, offvalue=False)
        # show_border_checkbox.grid(
        #     row=4, column=0, padx=10, pady=10, sticky='W')
        show_border_checkbox.grid(
            row=5, column=1, padx=10, pady=10, sticky='W')

    def device_index_update_callback(self, value):
        SUB.device_idx = value

    def device_index_get_callback(self):
        return SUB.device_idx

    def slider_event_x(self, value):
        self.sub_pos_x = value/100
        self.move_text(self.sub_pos_x, self.sub_pos_y)

    def slider_event_y(self, value):
        self.sub_pos_y = value/100
        self.move_text(self.sub_pos_x, self.sub_pos_y)

    def toggle_subtitle_button_callback(self):
        if self.subtitle_overlay is None or not self.subtitle_overlay.winfo_exists():
            # create window if its None or destroyed
            self.open_subtitle_overlay()
            self.toggle_overlay_button.configure(
                text="close overlay", fg_color='#fc7b5b')
        else:
            self.stop_subtitle_overlay()
            self.toggle_overlay_button.configure(
                text="start overlay", fg_color='grey')

    def open_subtitle_overlay(self):
        if self.subtitle_overlay is None or not self.subtitle_overlay.winfo_exists():
            # create window if its None or destroyed
            self.subtitle_overlay = SubtitleOverlay()
            SUB.start()
            SUB.text_change_eventhandlers.append(self.update_text)
            self.subtitle_overlay.overrideredirect(self.hide_border_var.get())
        else:
            self.subtitle_overlay.focus()  # if window exists focus it

    def stop_subtitle_overlay(self):
        if not (self.subtitle_overlay is None or not self.subtitle_overlay.winfo_exists()):
            SUB.stop()
            self.subtitle_overlay.destroy()

    def update_text(self, text):
        self.subtitle_overlay.label.configure(text=text)

    def move_text(self, x, y):
        self.subtitle_overlay.label.place(relx=x, rely=y, anchor='w')

    def update_phrase_max_length(self, value):
        SUB.m_phrase_time_limit = value
        self.phrase_max_length_label.configure(
            text=f'Phrase max length: {self.phrase_max_length_var.get()}')

    def set_show_border(self):
        if not (self.subtitle_overlay is None or not self.subtitle_overlay.winfo_exists()):
            # if subtitle_overlay exists
            self.subtitle_overlay.overrideredirect(self.hide_border_var.get())


class SubtitleOverlay(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.geometry("1920x1080+0+0")
        self.title("app")
        self.resizable(True, True)
        # self.overrideredirect(1)
        self.attributes("-topmost", True)
        self.wm_attributes('-transparentcolor', 'black')
        self.configure(fg_color='black')
        self.label = customtkinter.CTkLabel(
            master=self, text='default text', fg_color='black', text_color="white", font=("Arial", 45), wraplength=1500, anchor='w')
        self.label.place(relx=0.2, rely=0.8, anchor='w')


class OptionsFrame(customtkinter.CTkFrame):
    def __init__(self, master, enable_micmeter=True,  enable_input_language=True, **kwargs):
        super().__init__(master, **kwargs)
        self.speaker_names = STTS.get_speaker_names()
        self.default_speaker = self.speaker_names[0]
        self.current_speaker = self.default_speaker

        self.current_styles = STTS.get_speaker_styles(self.current_speaker)
        self.selected_style = self.current_styles[0]
        STTS.speaker_id = self.selected_style['id']

        if (enable_input_language):
            self.default_input_anguage = "English"
            self.input_anguage = ["English", "Japanese", "Chinese"]

            label_Input = customtkinter.CTkLabel(
                master=self, text='Input Language: ')
            label_Input.pack(padx=20, pady=10)
            input_language_combobox_var = customtkinter.StringVar(
                value=self.default_input_anguage)
            input_language_combobox = customtkinter.CTkComboBox(master=self,
                                                                values=self.input_anguage,
                                                                command=self.input_dropdown_callbakck,
                                                                variable=input_language_combobox_var)
            input_language_combobox.pack(padx=20, pady=0,)

        label_Input = customtkinter.CTkLabel(
            master=self, text='Speaker: ')
        label_Input.pack(padx=20, pady=10)
        speaker_combobox_var = customtkinter.StringVar(
            value=self.default_speaker)
        STTS.voice_name = self.default_speaker
        speaker_combobox = customtkinter.CTkComboBox(master=self,
                                                     values=self.speaker_names,
                                                     command=self.voice_dropdown_callbakck,
                                                     variable=speaker_combobox_var)
        speaker_combobox.pack(padx=20, pady=0)

        label_Input = customtkinter.CTkLabel(
            master=self, text='Style: ')
        label_Input.pack(padx=20, pady=10)
        self.style_combobox_var = customtkinter.StringVar(
            value=self.selected_style['name'])
        STTS.speaker_id = self.selected_style['id']
        self.style_combobox = customtkinter.CTkComboBox(master=self,
                                                        values=list(
                                                            map(lambda style: style['name'], self.current_styles)),
                                                        command=self.style_dropdown_callbakck,
                                                        variable=self.style_combobox_var)
        self.style_combobox.pack(padx=20, pady=0)

        self.audio_device_selection = AudiodeviceSelection(
            master=self, set_command=self.input_device_index_update_callback, get_command=self.input_device_index_get_callback, device_type='input', show_driver_selection=False, show_device_selection=False)
        self.audio_device_selection.pack(padx=20, pady=10)

    def input_device_index_update_callback(self, value):
        STTS.input_device_id = value

    def input_device_index_get_callback(self):
        return STTS.input_device_id

    def input_dropdown_callbakck(self, choice):
        STTS.change_input_language(choice)

    def voice_dropdown_callbakck(self, choice):
        self.current_speaker = choice
        self.current_styles = STTS.get_speaker_styles(self.current_speaker)
        self.style_combobox.configure(values=list(
            map(lambda style: style['name'], self.current_styles)))
        self.selected_style = self.current_styles[0]
        self.style_combobox_var = customtkinter.StringVar(
            value=self.selected_style['name'])
        self.style_combobox.configure(variable=self.style_combobox_var)
        STTS.speaker_id = self.selected_style['id']
        print(f'Changed speaker ID to: {STTS.speaker_id}')

    def style_dropdown_callbakck(self, choice):
        STTS.speaker_id = next(
            style['id'] for style in self.current_styles if choice == style['name'])
        print(f'Changed speaker ID to: {STTS.speaker_id}')


class Page(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        customtkinter.CTkFrame.__init__(self, *args, **kwargs)

    def show(self):
        self.lift()


class AudioInputPage(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        console = ConsoleFrame(master=self, width=500, corner_radius=8)
        console.grid(row=0, column=1, padx=20, pady=20,
                     sticky="nswe")
        options = OptionsFrame(master=self)
        options.grid(row=0, column=2, padx=20, pady=20, sticky="nswe")


class TextInputPage(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        textbox = TextBoxFrame(master=self, width=500, corner_radius=8)
        textbox.grid(row=0, column=1, padx=20, pady=20,
                     sticky="nswe")
        options = OptionsFrame(master=self)
        options.grid(row=0, column=2, padx=20, pady=20, sticky="nswe")


class SubtitlesPage(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        subtitles_frame = SubtitlesFrame(
            master=self, width=500, corner_radius=8)
        subtitles_frame.pack(padx=0, pady=0)


class ChatPage(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        chat_frame = ChatFrame(
            master=self, width=500, corner_radius=8)
        chat_frame.grid(row=0, column=1, padx=20, pady=20,
                        sticky="nswe")
        options = OptionsFrame(master=self, enable_input_language=False)
        options.grid(row=0, column=2, padx=20, pady=20, sticky="nswe")


class SettingsPage(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        mic_mode_label = customtkinter.CTkLabel(
            master=self, text='Microphone mode: ')
        mic_mode_label.grid(row=0, column=0, padx=10, pady=10, sticky='W')
        self.mic_mode_combobox_var = customtkinter.StringVar(
            value='open mic')
        self.mic_mode_combobox = customtkinter.CTkComboBox(master=self,
                                                           values=[
                                                               'open mic', 'push to talk'],
                                                           command=self.mic_mode_dropdown_callbakck,
                                                           variable=self.mic_mode_combobox_var)
        self.mic_mode_combobox.grid(
            row=0, column=1, padx=10, pady=10, sticky='W')
        self.mic_key_label = customtkinter.CTkLabel(
            master=self, text=f'push to talk key: {STTS.PUSH_TO_RECORD_KEY}')
        self.mic_key_label.grid(row=1, column=0, padx=10, pady=10, sticky='W')
        self.change_mic_key_Button = customtkinter.CTkButton(master=self,
                                                             text="change key",
                                                             command=self.change_push_to_talk_key,
                                                             fg_color='grey'
                                                             )
        self.change_mic_key_Button.grid(
            row=1, column=1, padx=10, pady=10, sticky='W')

        # self.label_gpu = customtkinter.CTkLabel(
        #     master=self, text=f'NVIDIA CUDA 11.7 active: {SUB.check_gpu_status()}')
        # self.label_gpu.grid(row=2, column=0, padx=10, pady=10, sticky='W')
        # self.label_gpu_help = customtkinter.CTkTextbox(
        #     master=self, width=300, height=100)
        # self.label_gpu_help.insert(
        #     "0.0", ('If you have a compatible NVIDIA GPU, you can download CUDA Toolkit to utilize your GPU: '
        #             'https://developer.nvidia.com/cuda-11-7-1-download-archive?target_os=Windows&target_arch=x86_64'))
        # self.label_gpu_help.configure(state='disabled')
        # self.label_gpu_help.grid(row=2, column=1, padx=10, pady=10, sticky='W')

        self.audio_device_selection = AudiodeviceSelection(
            master=self, set_command=self.input_device_index_update_callback, get_command=self.input_device_index_get_callback, device_type='input')
        self.audio_device_selection.grid(
            row=3, column=0, padx=10, pady=10, sticky='NW', rowspan=1, columnspan=2)
        self.audio_device_selection = AudiodeviceSelection(
            master=self, set_command=self.output_device_index_update_callback, get_command=self.output_device_index_get_callback, device_type='output')
        self.audio_device_selection.grid(
            row=3, column=1, padx=10, pady=10, sticky='NW', rowspan=1, columnspan=3)

        self.use_deepl_var = customtkinter.BooleanVar(
            self, translator.use_deepl)
        use_deepl_checkbox = customtkinter.CTkCheckBox(master=self, text="Use deepl (api key required)", command=self.set_use_deepl_var,
                                                       variable=self.use_deepl_var, onvalue=True, offvalue=False)
        use_deepl_checkbox.grid(row=4, column=0, padx=10, pady=10, sticky='W')
        self.deepl_api_key_var = customtkinter.StringVar(
            self, translator.deepl_api_key)
        self.deepl_api_key_var.trace_add('write', self.update_deepl_api_key)
        self.deepl_api_key_input = customtkinter.CTkEntry(
            master=self, textvariable=self.deepl_api_key_var)
        self.deepl_api_key_input.grid(
            row=4, column=1, padx=10, pady=10, sticky='W')

        self.use_voicevox_var = customtkinter.BooleanVar(
            self, STTS.use_cloud_voice_vox)
        use_voicevox_checkbox = customtkinter.CTkCheckBox(master=self, text="Use voicevox on cloud (api key optional)", command=self.set_use_voicevox_var,
                                                          variable=self.use_voicevox_var, onvalue=True, offvalue=False)
        use_voicevox_checkbox.grid(
            row=5, column=0, padx=10, pady=10, sticky='W')
        self.voicevox_api_key_var = customtkinter.StringVar(
            self, STTS.voice_vox_api_key)
        self.voicevox_api_key_var.trace_add(
            'write', self.update_voicevox_api_key)
        self.voicevox_api_key_input = customtkinter.CTkEntry(
            master=self, textvariable=self.voicevox_api_key_var)
        self.voicevox_api_key_input.grid(
            row=5, column=1, padx=10, pady=10, sticky='W')

        self.label_openai_api_key = customtkinter.CTkLabel(
            master=self, text=f'Open-AI API key(required to chat): ')
        self.label_openai_api_key.grid(
            row=6, column=0, padx=10, pady=10, sticky='W')
        self.openai_api_key_var = customtkinter.StringVar(
            self, chatbot.openai_api_key)
        self.openai_api_key_var.trace_add(
            'write', self.update_openai_api_key)
        self.openai_api_key_input = customtkinter.CTkEntry(
            master=self, textvariable=self.openai_api_key_var)
        self.openai_api_key_input.grid(
            row=6, column=1, padx=10, pady=10, sticky='W')

    def input_device_index_update_callback(self, value):
        STTS.input_device_id = value

    def input_device_index_get_callback(self):
        return STTS.input_device_id

    def output_device_index_update_callback(self, value):
        STTS.output_device_id = value

    def output_device_index_get_callback(self):
        return STTS.output_device_id

    def mic_mode_dropdown_callbakck(self, choice):
        STTS.mic_mode = choice

    def set_use_deepl_var(self):
        translator.use_deepl = self.use_deepl_var.get()
        STTS.save_config('use_deepl', translator.use_deepl)

    def update_deepl_api_key(self, str1, str2, str3):
        translator.deepl_api_key = self.deepl_api_key_var.get()
        STTS.save_config('deepl_api_key', translator.deepl_api_key)

    def set_use_voicevox_var(self):
        print(f'use_cloud_voice_vox set to {self.use_voicevox_var.get()}')
        STTS.use_cloud_voice_vox = self.use_voicevox_var.get()
        STTS.save_config('use_cloud_voice_vox', STTS.use_cloud_voice_vox)

    def update_voicevox_api_key(self, str1, str2, str3):
        STTS.voice_vox_api_key = self.voicevox_api_key_var.get()
        STTS.save_config('voice_vox_api_key', STTS.voice_vox_api_key)

    def update_openai_api_key(self, str1, str2, str3):
        chatbot.openai_api_key = self.openai_api_key_var.get()
        STTS.save_config('openai_api_key', chatbot.openai_api_key)

    def change_push_to_talk_key(self):
        thread = Thread(target=self.listen_for_key)
        thread.start()

    def listen_for_key(self):
        self.mic_key_label.configure(text='listening to keypress...')
        self.change_mic_key_Button.configure(fg_color='#fc7b5b')
        key = keyboard.read_key()
        STTS.PUSH_TO_RECORD_KEY = key
        self.mic_key_label.configure(
            text=f'push to talk key: {STTS.PUSH_TO_RECORD_KEY}')
        self.change_mic_key_Button.configure(fg_color='grey')


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("850x500")
        self.title("Voice to Japanese")
        self.resizable(False, False)

        sidebar = SidebarFrame(master=self, width=100)
        sidebar.grid(row=0, column=0, padx=20, pady=20, sticky="nswe")

        audioInputPage = AudioInputPage(self)
        textInputPage = TextInputPage(self)
        settingsPage = SettingsPage(self)
        subtitlesPage = SubtitlesPage(self)
        chatPage = ChatPage(self)
        container = customtkinter.CTkFrame(
            self, width=700, height=700, bg_color='#fafafa')
        container.grid(row=0, column=1, padx=20, pady=20, sticky="nswe")

        audioInputPage.place(in_=container, x=0, y=0)
        textInputPage.place(in_=container, x=0, y=0)
        subtitlesPage.place(in_=container, x=0, y=0)
        chatPage.place(in_=container, x=0, y=0)
        settingsPage.place(in_=container, x=0, y=0)

        audioInputPage.show()
        global pageChange_eventhandlers

        def showPage():
            global current_page
            if (current_page == Pages.AUDIO_INPUT):
                container.lift()
                audioInputPage.show()
            elif (current_page == Pages.TEXT_INPUT):
                container.lift()
                textInputPage.show()
            elif (current_page == Pages.SUBTITLE):
                container.lift()
                subtitlesPage.show()
            elif (current_page == Pages.SETTINGS):
                container.lift()
                settingsPage.show()
            elif (current_page == Pages.CHAT):
                container.lift()
                chatPage.show()
        pageChange_eventhandlers.append(showPage)


def optionmenu_callback(choice):
    print("optionmenu dropdown clicked:", choice)


def print_sound(indata, outdata, frames, time, status):
    global audio_level
    audio_level = np.linalg.norm(indata)/10
    # print("|" * int(volume_norm))


def listen_to_mic():
    with sd.Stream(callback=print_sound):
        sd.sleep(10000000)


thread = Thread(target=listen_to_mic)
thread.start()

print("Starting voicevox server...")
STTS.start_voicevox_server()
print("Initializing tts model...")
STTS.initialize_model()
print("Initializing translator...")
translator.initialize()
print("loading config... ")
STTS.load_config()

app = App()
app.configure(background='#fafafa')
app.mainloop()
