import customtkinter
import SUB
from threading import Thread


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1920x1080+0+0")
        self.title("Voice to Japanese")
        self.resizable(False, False)
        self.label = customtkinter.CTkLabel(
            master=self, text='Hello this is a test', fg_color='black', text_color="white", font=("Arial", 25))
        self.label.place(relx=0.5, rely=0.8, anchor=customtkinter.CENTER)


class Config(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("300x600")
        self.title("Voice to Japanese")
        self.resizable(False, False)
        self.label = customtkinter.CTkLabel(
            master=self, text='Hello this is a test', fg_color='black', text_color="white", font=("Arial", 45))
        self.label.place(relx=0.5, rely=0.8, anchor=customtkinter.CENTER)


app = App()


def update_text(text):
    app.label.configure(text=text)


SUB.text_change_eventhandlers.append(update_text)

app.title("123")
app.overrideredirect(1)
app.wm_attributes('-transparentcolor', 'black')
app.configure(fg_color='black')

thread = Thread(target=SUB.start_translator)
thread.start()
app.mainloop()
