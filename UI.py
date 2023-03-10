from threading import Thread
import customtkinter
import STTS
from threading import Event
from enum import Enum


class Pages(Enum):
    AUDIO_INPUT = 0
    TEXT_INPUT = 1
    SETTINGS = 2


current_page = Pages.AUDIO_INPUT
pageChange_eventhandlers = []


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


class OptionsFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.default_voice = "???????????????"
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

        label_Input = customtkinter.CTkLabel(
            master=self, text='Voice: ')
        label_Input.pack(padx=20, pady=10)
        combobox_var = customtkinter.StringVar(
            value=self.default_voice)
        STTS.voice_name = self.default_voice
        combobox = customtkinter.CTkComboBox(master=self,
                                             values=self.voicenames,
                                             command=self.voice_dropdown_callbakck,
                                             variable=combobox_var)
        combobox.pack(padx=20, pady=10)

    def input_dropdown_callbakck(self, choice):
        STTS.change_input_language(choice)

    def voice_dropdown_callbakck(self, choice):
        STTS.voice_name = choice


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


class SettingsPage(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.use_local_voice_vox = customtkinter.BooleanVar(self, 1)
        self.check_var = customtkinter.BooleanVar(self, False)

        use_voicevox_local_checkbox = customtkinter.CTkCheckBox(master=self, text="Is running voicevox locally", command=self.set_use_voicevox_local,
                                                                variable=self.check_var, onvalue=True, offvalue=False)
        use_voicevox_local_checkbox.pack(padx=20, pady=10)

    def set_use_voicevox_local(self):
        STTS.use_local_voice_vox = self.check_var.get()


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
        container = customtkinter.CTkFrame(
            self, width=700, height=700, bg_color='#fafafa')
        container.grid(row=0, column=1, padx=20, pady=20, sticky="nswe")

        audioInputPage.place(in_=container, x=0, y=0)
        textInputPage.place(in_=container, x=0, y=0)
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
            elif (current_page == Pages.SETTINGS):
                container.lift()
                settingsPage.show()
        pageChange_eventhandlers.append(showPage)


def optionmenu_callback(choice):
    print("optionmenu dropdown clicked:", choice)


app = App()
app.configure(background='#fafafa')
app.mainloop()
