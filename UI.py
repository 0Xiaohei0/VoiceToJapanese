import customtkinter


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
        # add widgets onto the frame...
        textbox = customtkinter.CTkTextbox(self, width=400, height=400)
        textbox.grid(row=0, column=0, rowspan=2, columnspan=2)
        # insert at line 0 character 0
        textbox.insert("0.0", "new text to insert")
        # configure textbox to be read-only
        textbox.configure(state="disabled")

        button = customtkinter.CTkButton(master=self,
                                         width=120,
                                         height=32,
                                         border_width=0,
                                         corner_radius=8,
                                         text="Start Recording",
                                         fg_color='grey'
                                         )
        button.grid(row=3, column=0, pady=10)

        button1 = customtkinter.CTkButton(master=self,
                                          width=120,
                                          height=32,
                                          border_width=0,
                                          corner_radius=8,
                                          text="Play original",
                                          fg_color='grey'
                                          )
        button1.grid(row=3, column=1, pady=10)


class OptionsFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        label_Input = customtkinter.CTkLabel(
            master=self, text='Input Language: ')
        label_Input.pack(padx=20, pady=10)
        combobox_var = customtkinter.StringVar(value="Auto")
        combobox = customtkinter.CTkComboBox(master=self,
                                             values=["Auto", "option 2"],
                                             command=self.combobox_callback,
                                             variable=combobox_var)
        combobox.pack(padx=20, pady=10,)

        label_Output = customtkinter.CTkLabel(
            master=self, text='Output Language: ')
        label_Output.pack(padx=20)
        combobox_var = customtkinter.StringVar(
            value="Auto")
        combobox = customtkinter.CTkComboBox(master=self,
                                             values=["Auto", "option 2"],
                                             command=self.combobox_callback,
                                             variable=combobox_var)
        combobox.pack(padx=20, pady=10)

        label_Output = customtkinter.CTkLabel(
            master=self, text='Voice: ')
        label_Output.pack(padx=20)
        combobox_var = customtkinter.StringVar(
            value="option 2")
        combobox = customtkinter.CTkComboBox(master=self,
                                             values=["Auto", "option 2"],
                                             command=self.combobox_callback,
                                             variable=combobox_var)
        combobox.pack(padx=20, pady=10)

    def combobox_callback(choice):
        print("combobox dropdown clicked:", choice)


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
        # self.consoleFrame = ConsoleFrame(
        #     master=self, width=2000, height=200, border_width=100, border_color='red')
        # self.consoleFrame.grid(row=0, column=0, rowspan=2,
        #                        columnspan=2, padx=20, pady=20)

        # self.sidebarFrame = SidebarFrame(master=self)
        # self.sidebarFrame.grid(row=0, column=0, padx=20, rowspan=4,
        #                        pady=20, sticky="nswe")

    # add methods to app
    def button_click(self):
        print("button click")

    def optionmenu_callback(choice):
        print("optionmenu dropdown clicked:", choice)


app = App()
app.mainloop()
