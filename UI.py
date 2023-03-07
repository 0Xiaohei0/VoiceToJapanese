from threading import Thread
import customtkinter
import STTS
from threading import Event


class SidebarFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        button = customtkinter.CTkButton(master=self,
                                         width=120,
                                         height=32,
                                         border_width=0,
                                         corner_radius=0,
                                         text="Main",
                                         fg_color='grey'
                                         )
        button.pack(anchor="s")
        # add widgets onto the frame...
        button = customtkinter.CTkButton(master=self,
                                         width=120,
                                         height=32,
                                         border_width=0,
                                         corner_radius=0,
                                         text="Settings",
                                         fg_color='grey'
                                         )
        button.pack(anchor="s")


class ConsoleFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.isRecording = False
        self.stop_recording_event = Event()
        self.thread = Thread(target=STTS.start_record_auto,
                             args=(self.stop_recording_event,))
        # add widgets onto the frame...
        self.textbox = customtkinter.CTkTextbox(self, width=400, height=400)
        self.textbox.grid(row=0, column=0, rowspan=2, columnspan=2)
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

    def recordButton_callback(self):
        if (self.isRecording):
            self.recordButton.configure(
                text="Start Recording", fg_color='grey')
            self.isRecording = False
            self.stop_recording_event.set()
            STTS.stop_record_auto()
        else:
            self.recordButton.configure(
                text="Stop Recording", fg_color='#fc7b5b')
            self.isRecording = True
            self.stop_recording_event.clear()
            self.thread = Thread(target=STTS.start_record_auto,
                                 args=(self.stop_recording_event,))
            self.thread.start()
        self.recordButton.grid(row=3, column=0, pady=10)

    def play_original_callback(self):
        STTS.playOriginal()

    def log_message_on_console(self, message_text):
        # insert at line 0 character 0
        self.textbox.configure(state="normal")
        self.textbox.insert(customtkinter.INSERT, message_text+'\n')
        self.textbox.configure(state="disabled")


class OptionsFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.default_voice = "四国めたん"
        self.voicenames = list(STTS.voicename_to_callparam_dict.keys())

        self.default_input_anguage = "English"
        self.input_anguage = ["English", "Japanese", "Chinese"]

        label_Input = customtkinter.CTkLabel(
            master=self, text='Input Language: ')
        label_Input.pack(padx=20, pady=10)
        combobox_var = customtkinter.StringVar(
            value=self.default_input_anguage)
        combobox = customtkinter.CTkComboBox(master=self,
                                             values=self.input_anguage,
                                             command=self.input_dropdown_callbakck,
                                             variable=combobox_var)
        combobox.pack(padx=20, pady=10,)

        combobox_var = customtkinter.StringVar(
            value=self.default_voice)
        STTS.voice_name = self.default_voice
        combobox = customtkinter.CTkComboBox(master=self,
                                             values=self.voicenames,
                                             command=self.voice_dropdown_callbakck,
                                             variable=combobox_var)
        combobox.pack(padx=20, pady=10)

    def input_dropdown_callbakck(self, choice):
        STTS.input_language_name = choice

    def voice_dropdown_callbakck(self, choice):
        STTS.voice_name = choice


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("850x500")
        self.title("CTk example")
        self.resizable(False, False)

        sidebar = SidebarFrame(master=self, width=100)
        sidebar.grid(row=0, column=0, padx=20, pady=20, sticky="nswe")

        console = ConsoleFrame(master=self, width=500, corner_radius=8)
        console.grid(row=0, column=1, padx=20, pady=20,
                     sticky="nswe")

        options = OptionsFrame(master=self)
        options.grid(row=0, column=2, padx=20, pady=20, sticky="nswe")


def optionmenu_callback(choice):
    print("optionmenu dropdown clicked:", choice)


app = App()
app.mainloop()
