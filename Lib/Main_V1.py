import json
import logging
import os
import time
import tkinter as tk
import urllib.request
import urllib.request
from threading import Timer
from tkinter import ttk
from tkinter.ttk import Notebook, Style
import cv2 as cv
import pyvisa
from PIL import Image
from PIL import ImageTk
from pygame import mixer
from tkinter import messagebox
import sys

with open('Setting Paramiter.json', 'r') as json_file:
    Setting_Paramiter = json.loads(json_file.read())
Quantity_Cam = Setting_Paramiter[0]["Quantity_Cam"]
Board_Name = Setting_Paramiter[0]["Board_Name"]
Machine = Setting_Paramiter[0]["MachineName"]
#AutoFocus_1 = Setting_Paramiter[0]["AutoFocus_1"]
#AutoFocus_2 = Setting_Paramiter[0]["AutoFocus_2"]

if Quantity_Cam == 1:
    frame0 = cv.VideoCapture(0, cv.CAP_DSHOW)
    frame0.set(cv.CAP_PROP_FRAME_WIDTH, 1024)
    frame0.set(cv.CAP_PROP_FRAME_HEIGHT, 768)
    frame0.set(cv.CAP_PROP_AUTO_EXPOSURE,0)
    frame0.set(cv.CAP_PROP_AUTOFOCUS, 0)
elif Quantity_Cam == 2:
    frame0 = cv.VideoCapture(0, cv.CAP_DSHOW)
    frame0.set(cv.CAP_PROP_FRAME_WIDTH, 1024)
    frame0.set(cv.CAP_PROP_FRAME_HEIGHT, 768)
    frame0.set(cv.CAP_PROP_AUTO_EXPOSURE, 0)
    frame0.set(cv.CAP_PROP_AUTOFOCUS, 0)
    frame1 = cv.VideoCapture(1, cv.CAP_DSHOW)
    frame1.set(cv.CAP_PROP_FRAME_WIDTH, 1024)
    frame1.set(cv.CAP_PROP_FRAME_HEIGHT, 768)
    frame1.set(cv.CAP_PROP_AUTO_EXPOSURE, 0)
    frame1.set(cv.CAP_PROP_AUTOFOCUS, 0)
font = cv.FONT_HERSHEY_SIMPLEX

def Save_Result(Data):
    item = [{'Result': Data}]
    with open('Result.json', 'w') as json_file:
        json.dump(item, json_file)


class Getpart():
    def __init__(self):
        self.Sever = None

    def __int__(self):
        # with open('GetPart_API.txt', 'r') as API_Part:
        # self.Part_Paramiter = API_Part.read()
        self.Part_Paramiter = "http://192.168.1.48:89/RobotAPI/GetPart?machineId=" + Machine + ""

    def Get(self):
            try:
                with urllib.request.urlopen(self.Part_Paramiter, timeout=5) as response:
                    json_API = json.loads(response.read())
                self.Sever = "Connected"
                self.PartNumber = json_API[0]["PartNumber"]
                self.BatchNumber = json_API[0]["BatchNumber"]
                self.PartName = json_API[0]["PartName"]
                self.CustomerPartNumber = json_API[0]["CustomerPartNumber"]
                self.MachineName = json_API[0]["MachineName"]
                self.MoldId = json_API[0]["MoldId"]
                self.Packing = json_API[0]["PackingStd"]
                with open('Part.json', 'w') as Keep_Part:
                    json.dump(json_API, Keep_Part, indent=6)
            except:
                with open('Part.json', 'r') as json_Part:
                    json_Part_Disconnet = json.loads(json_Part.read())
                self.Sever = "Disconnect"
                self.PartNumber = json_Part_Disconnet[0]["PartNumber"]
                self.BatchNumber = json_Part_Disconnet[0]["BatchNumber"]
                self.PartName = json_Part_Disconnet[0]["PartName"]
                self.CustomerPartNumber = json_Part_Disconnet[0]["CustomerPartNumber"]
                self.MachineName = json_Part_Disconnet[0]["MachineName"]
                self.MoldId = json_Part_Disconnet[0]["MoldId"]
                self.Packing = json_Part_Disconnet[0]["PackingStd"]
            return [self.PartNumber, self.BatchNumber, self.PartName, self.CustomerPartNumber, self.MachineName,
                    self.MoldId, self.Sever, self.Packing]



class GetEmp():
    def __int__(self):
        dirName = 'Information'
        try:
            os.mkdir(dirName)
        except FileExistsError:
            pass

        try:
            with urllib.request.urlopen("http://192.168.1.48:89/RobotAPI/GetEmp") as response:
                json_Emp = json.loads(response.read())
            with open('Information/Operator.json', 'w') as Operator:
                json.dump(json_Emp, Operator, indent=6)
        except:
            pass


class Borad():
    def __init__(self):
        super().__init__()
        self.data = None
        self.Read_Board = None
        self.rm = pyvisa.ResourceManager()
        self.address = Board_Name
        self.inst = self.rm.open_resource(self.address)
        self.inst.clear()

    def ReadBorad(self):
        self.inst.write("@1 I0")
        self.inst.query("*IDN?")
        self.Read_Board = self.inst.read()
        self.Read_Board = str(self.Read_Board)
        # self.Board.configure(text=Read_Board)
        self.data = self.Read_Board.split("#")
        self.data = bytes(self.data[1], "ascii")
        self.data = "{:08b}".format(int(self.data.hex(), 16))
        """""
        if self.data == "110000001100010000110100001010":  # 01
            self.inst.write("@1 R20")
        elif self.data == "110000001100100000110100001010":  # 02
            self.inst.write("@1 R00")
        """""
        return [self.Read_Board, self.inst.write]


class InfiniteTimer():
    """A Timer class that does not stop, unless you want it to."""

    def __init__(self, seconds, target):
        self._should_continue = False
        self.is_running = False
        self.seconds = seconds
        self.target = target
        self.thread = None

    def _handle_target(self):
        self.is_running = True
        self.target()
        self.is_running = False
        self._start_timer()

    def _start_timer(self):
        if self._should_continue:  # Code could have been running when cancel was called.
            self.thread = Timer(self.seconds, self._handle_target)
            self.thread.start()

    def start(self):
        if not self._should_continue and not self.is_running:
            self._should_continue = True
            self._start_timer()
        else:
            print("Timer already started or running, please wait if you're restarting.")

    def cancel(self):
        if self.thread is not None:
            self._should_continue = False  # Just in case thread is running and cancel fails.
            self.thread.cancel()
        else:
            print("Timer never started or failed to initialize.")

class App(tk.Tk, Getpart):
    def __init__(self):
        super().__init__()
        GetEmp().__int__()
        style = Style()
        # style.theme_create("MyStyle", parent="default", settings={"TNotebook.Tab": {"configure": {"padding": [25, 10] ,"font": 20}, }})

        # style.theme_settings(themename="default", settings={"TNotebook.Tab": {"configure": {"padding": [25, 50] ,"font": 20}}})
        # style.theme_create("MyStyle", parent="default", settings={
        #   "TNotebook": {"configure": {"tabmargins": [0, 0, 0, 0]}},
        #  "TNotebook.Tab": {"configure": {"padding": [10, 10],
        #                                 "font": ('Arial', '20', 'bold'),
        #                                "foreground": ('Green')},}})
        # style.theme_use("MyStyle")
        # configure the root window

        ttk.Style().configure('TNotebook.Tab', font=('Arial', 20),
                              background='black', foreground='#006400', borderwidth=0)

        self.title('Machine Vision Inspection 1.4.0')
        self.geometry("1920x1020+0+0")
        #self.state('zoomed')
        self.attributes('-fullscreen', True)

        self.notebook = ttk.Notebook(self)

        self.Frame1 = Frame1(self.notebook)
        self.Frame2 = Frame2(self.notebook)
        self.Frame1.configure(width=1920, height=1020)
        self.Frame2.configure(width=1920, height=1020)
        self.notebook.add(self.Frame1, text='Main')
        self.notebook.add(self.Frame2, text='Add/Edit')
        self.notebook.place(x=1, y=1)
        self.notebook.bind("<<NotebookTabChanged>>", self.handle_tab_changed)

    def handle_tab_changed(self, event):
        selection = event.widget.select()
        tab = event.widget.tab(selection, "text")
        item = [{'Status': tab}]
        with open('Status .json', 'w') as json_file:
            json.dump(item, json_file)
        if tab == "Main":
            self.Frame1.focus_set()

        else:
            self.Frame2.focus_set()


class Frame1(ttk.Frame, App):
    def __init__(self, container):
        self.API_json = Getpart()
        self.API_json.__int__()
        self.Part_API = self.API_json.Get()[0]
        self.Batch_API = self.API_json.Get()[1]
        self.part_name_API = self.API_json.Get()[2]
        self.Customer_API = self.API_json.Get()[3]
        self.Machine_API = self.API_json.Get()[4]
        self.Mode_API = self.API_json.Get()[5]
        self.Sever_API = self.API_json.Get()[6]
        self.Packing_API = self.API_json.Get()[7]

        self.Batch_API_Get = self.Batch_API
        super().__init__()
        self.Run_Alarm = None
        self.count = 0
        self.update_image = None
        self.Printer = 0

        self.combobox_cam()
        self.btn_cam = tk.Button(self, text="Choose Camera", command=self.callback_cam)
        self.btn_cam.configure(font=("Arial", 13))
        self.btn_cam.configure(justify="center", foreground="green")
        self.btn_cam.place(x=650, y=20)

        self.btn_reset = tk.Button(self, text="Initiated", command=self.ShowCount)
        self.btn_reset.configure(font=("Arial", 13))
        self.btn_reset.configure(justify="center", foreground="green")
        self.btn_reset.place(x=800, y=20)

        self.btn_Close = tk.Button(self, text="Close", command=self.Destroy)
        self.btn_Close.configure(font=("Arial", 15))
        self.btn_Close.configure(justify="center", foreground="red")
        self.btn_Close.place(x=1850, y=2)

        # self.thread = VideoThread()
        # self.thread.start()
        # self.thread.run()

        # self.l2.place(x=10, y=15)

        # button
        # self.button = tk.Button(self, text='Save')
        # self.button['command'] = self.SaveImage
        # self.button.place(x=800, y=20)

        # NG OR OK Show
        self.Batch_API = self.API_json.Get()[1]
        self.Batch_API_Get = self.Batch_API
        self.Machine_Vision = tk.Label(self, text='Machine Vision Inspection')
        self.Machine_Vision.configure(font=("Arial", 30))
        self.Machine_Vision.configure(fg=('Green'))
        self.Machine_Vision.place(x=15, y=5)

        self.Machine_Version = tk.Label(self, text='v1.0.4')
        self.Machine_Version.configure(font=("Arial", 10))
        self.Machine_Version.configure(fg=('Green'))
        self.Machine_Version.place(x=15, y=45)

        self.Machine = tk.LabelFrame(self, text="MACHINE")
        self.Machine.configure(font=("Arial", 13))
        self.Machine.configure(fg='Green')
        self.Machine.place(x=15, y=70, height=60, width=180)
        self.MachineP = tk.Label(self.Machine, text=self.Machine_API)
        self.MachineP.configure(font=("Arial", 20))
        self.MachineP.configure(fg='Green')
        self.MachineP.place(x=10, y=15, anchor=tk.W)

        self.PART = tk.LabelFrame(self, text="BKF PART NUMBER")
        self.PART.configure(font=("Arial", 13))
        self.PART.configure(fg='Green')
        self.PART.place(x=215, y=70, height=60, width=180)
        self.PARTP = tk.Label(self.PART, text=self.Part_API)
        self.PARTP.configure(font=("Arial", 13))
        self.PARTP.configure(fg='Green')
        self.PARTP.place(x=10, y=15, anchor=tk.W)

        self.PART_NAME = tk.LabelFrame(self, text="PART NAME")
        self.PART_NAME.configure(font=("Arial", 13))
        self.PART_NAME.configure(fg='Green')
        self.PART_NAME.place(x=415, y=70, height=60, width=500)
        self.PART_NAMEP = tk.Label(self.PART_NAME, text=self.part_name_API)
        self.PART_NAMEP.configure(font=("Arial", 13))
        self.PART_NAMEP.configure(fg='Green')
        self.PART_NAMEP.place(x=10, y=15, anchor=tk.W)

        self.Sever = tk.LabelFrame(self, text="Sever")
        self.Sever.configure(font=("Arial", 13))
        self.Sever.configure(fg='Green')
        self.Sever.place(x=935, y=70, height=60, width=120)
        self.SeverP = tk.Label(self.Sever, text=self.Sever_API)
        self.SeverP.configure(font=("Arial", 13))
        if self.Sever_API == "Connected":
            self.SeverP.configure(fg='Green')
        else:
            self.SeverP.configure(fg='Red')
        self.SeverP.place(x=10, y=15, anchor=tk.W)

        # self.Board = tk.Label(self)
        # self.Board.grid(padx=200, pady=500)
        # self.Board.configure(font=("Courier", 44))
        # self.filemenu.add_command(label="New...", command=self.Img_part())
        self.Img_part()

        self.CUSTOMER_NUMBER = tk.LabelFrame(self, text="CUSTOMER NUMBER")
        self.CUSTOMER_NUMBER.configure(font=("Arial", 13))
        self.CUSTOMER_NUMBER.configure(fg='Green')
        self.CUSTOMER_NUMBER.place(x=15, y=150, height=60, width=180)
        self.CUSTOMER_NUMBERP = tk.Label(self.CUSTOMER_NUMBER, text=self.Customer_API)
        self.CUSTOMER_NUMBERP.configure(font=("Arial", 13))
        self.CUSTOMER_NUMBERP.configure(fg='Green')
        self.CUSTOMER_NUMBERP.place(x=10, y=15, anchor=tk.W)

        self.BATCH_NUMBER = tk.LabelFrame(self, text="BATCH NUMBER")
        self.BATCH_NUMBER.configure(font=("Arial", 13))
        self.BATCH_NUMBER.configure(fg='Green')
        self.BATCH_NUMBER.place(x=215, y=150, height=60, width=180)
        self.BATCH_NUMBERP = tk.Label(self.BATCH_NUMBER, text=self.Batch_API)
        self.BATCH_NUMBERP.configure(font=("Arial", 13))
        self.BATCH_NUMBERP.configure(fg='Green')
        self.BATCH_NUMBERP.place(x=10, y=15, anchor=tk.W)

        self.MOLD_NUMBER = tk.LabelFrame(self, text="MOLD NUMBER")
        self.MOLD_NUMBER.configure(font=("Arial", 13))
        self.MOLD_NUMBER.configure(fg='Green')
        self.MOLD_NUMBER.place(x=415, y=150, height=60, width=180)
        self.MOLD_NUMBERP = tk.Label(self.MOLD_NUMBER, text=self.Mode_API)
        self.MOLD_NUMBERP.configure(font=("Arial", 13))
        self.MOLD_NUMBERP.configure(fg='Green')
        self.MOLD_NUMBERP.place(x=10, y=15, anchor=tk.W)

        self.OK_Data = 0
        self.NG_Data = 0
        self.Comfrim_Data = 0
        self.Comfrim_SaveScore = 0
        self.OK = tk.LabelFrame(self, text="OK", borderwidth=3, relief="ridge", padx=5, pady=10)
        self.OK.configure(font=("Arial", 25))
        self.OK.configure(fg='Green')
        self.OK.place(x=1280, y=50, height=130, width=250)

        self.Result_Ok = tk.Label(self.OK, text=self.OK_Data, borderwidth=3, relief="ridge", padx=5, pady=10)
        self.Result_Ok.configure(font=("Arial", 25))
        self.Result_Ok.configure(fg='Green')
        self.Result_Ok.place(x=15, y=0, height=70, width=200)

        self.NG = tk.LabelFrame(self, text="NG", borderwidth=3, relief="ridge", padx=5, pady=10)
        self.NG.configure(font=("Arial", 25))
        self.NG.configure(fg='Red')
        self.NG.place(x=1580, y=50, height=130, width=250)

        self.Result_NG = tk.Label(self.NG, text=self.NG_Data, borderwidth=3, relief="ridge", padx=5, pady=10)
        self.Result_NG.configure(font=("Arial", 25))
        self.Result_NG.configure(fg='Red')
        self.Result_NG.place(x=15, y=0, height=70, width=200)

        self.Label_cam = tk.Label(self, text="Cam1")
        self.frame = tk.Label(self)
        self.frame.place(x=615, y=550)

        self.view1 = tk.Label(self)
        self.view1.place(x=1280, y=205)
        self.view2 = tk.Label(self)
        self.view2.place(x=1280, y=605)

        self.Process = tk.LabelFrame(self, text="Process")
        self.Process.configure(font=("Arial", 13))
        self.Process.configure(fg='Green')
        self.Process.place(x=1085, y=70, height=60, width=120)
        self.ProcessP = tk.Label(self.Process, text="Ready", fg='Green')
        self.ProcessP.configure(font=("Arial", 18))
        self.ProcessP.place(x=10, y=15, anchor=tk.W)

        self.Img_part()
        self.PrintText()
        self.Camera()
        self.ShowCount()
        self.CallKeyBorad()
        self.f = True

        self.btn_repart = tk.Button(self, text="Repart", command=self.CallPart)
        self.btn_repart.configure(font=("Arial", 15))
        self.btn_repart.configure(justify="center", foreground="green")
        self.btn_repart.place(x=1750, y=2)

        # self.Board_show()

        # self.Board = InfiniteTimer(0.5, self.Board_show)
        # self.Board.start()
        # self.ShowPoint()

        # self.thread = threading.Timer(0.1,self.RunCam())
        # self.thread.start()

        # Camera = InfiniteTimer(0.001, self.Camera)
        # Camera.start()
        # self.SaveImage()

    # def button_clicked(self):
    # showinfo(title='Information', message='Hello, Tkinter!')
    # def tick(self):
    # print('ipsem lorem')
    # self.notebook.bind_all("<<NotebookTabChanged>>", self.xxx)
    # self.notebook.bind("<<NotebookTabChanged>>")


    def CallPart(self):
        self.API_json = Getpart()
        self.API_json.__int__()
        self.Part_API = self.API_json.Get()[0]
        self.Batch_API = self.API_json.Get()[1]
        self.part_name_API = self.API_json.Get()[2]
        self.Customer_API = self.API_json.Get()[3]
        self.Machine_API = self.API_json.Get()[4]
        self.Mode_API = self.API_json.Get()[5]
        self.Sever_API = self.API_json.Get()[6]
        self.Packing_API = self.API_json.Get()[7]

        if self.Batch_API_Get == self.Batch_API:
            pass
        elif self.Batch_API_Get != self.Batch_API:
            self.Batch_API_Get = self.Batch_API
            self.MachineP.configure(text=self.Machine_API)
            self.PARTP.configure(text=self.Part_API)
            self.PART_NAMEP.configure(text=self.part_name_API)
            self.CUSTOMER_NUMBERP.configure(text=self.Customer_API)
            self.BATCH_NUMBERP.configure(text=self.Batch_API)
            self.MOLD_NUMBERP.configure(text=self.Mode_API)
            self.Img_part()
            self.ShowCount()
            self.PrintText()

    def ShowCount(self):
        self.OK_Data = 0
        self.NG_Data = 0
        self.Result_Ok.configure(text=self.OK_Data)
        self.Result_NG.configure(text=self.NG_Data)
        self.Alarm(True)
        self.Speaker = True

        Save_Result(1)
        self.btn_reset.focus_set()
        self.Point_ = tk.LabelFrame(self, text="Point", borderwidth=3, relief="ridge", padx=5, pady=10)
        self.Point_.configure(font=("Arial", 13))
        self.Point_.configure(fg='Green')
        self.Point_.place(x=15, y=230, height=740, width=135)

        self.Result_ = tk.LabelFrame(self, text="Result", borderwidth=3, relief="ridge", padx=5, pady=10)
        self.Result_.configure(font=("Arial", 13))
        self.Result_.configure(fg='Green')
        self.Result_.place(x=165, y=230, height=740, width=135)

        self.Score_Outline = tk.LabelFrame(self, text="Score Outline", borderwidth=3, relief="ridge", padx=5, pady=10)
        self.Score_Outline.configure(font=("Arial", 13))
        self.Score_Outline.configure(fg='Green')
        self.Score_Outline.place(x=315, y=230, height=740, width=135)

        self.Score_Area = tk.LabelFrame(self, text="Score Area", borderwidth=3, relief="ridge", padx=5, pady=10)
        self.Score_Area.configure(font=("Arial", 13))
        self.Score_Area.configure(fg='Green')
        self.Score_Area.place(x=465, y=230, height=740, width=135)
        try:
            self.dir_path = r"" + self.Part_API + "\Master"
            self.count = 0
            for path in os.listdir(self.dir_path):
                if os.path.isfile(os.path.join(self.dir_path, path)):
                    if path.endswith('.bmp'):
                        self.count += 1
        except:
            self.count = 0
        try:
            with open('Master_' + self.Part_API + '.json', 'r') as json_file:
                self.Master = json.loads(json_file.read())
            if self.count != 0:
                self.Point_Camera = []
                self.Point_Left = []
                self.Point_Top = []
                self.Point_Right = []
                self.Point_Bottom = []
                self.Point_Score_Outline = []
                self.Point_Score_Area = []
                for k in range(self.count):
                    self.Point_Camera.append(self.Master[k]["Point" + str(k + 1)][0]["Camera"])
                    self.Point_Left.append(self.Master[k]["Point" + str(k + 1)][0]["Left"])
                    self.Point_Top.append(self.Master[k]["Point" + str(k + 1)][0]["Top"])
                    self.Point_Right.append(self.Master[k]["Point" + str(k + 1)][0]["Right"])
                    self.Point_Bottom.append(self.Master[k]["Point" + str(k + 1)][0]["Bottom"])
                    self.Point_Score_Outline.append(self.Master[k]["Point" + str(k + 1)][0]["Score Outline"])
                    self.Point_Score_Area.append(self.Master[k]["Point" + str(k + 1)][0]["Score Area"])

                    tk.Label(self.Point_, text="Point" + str(k + 1), borderwidth=3, relief="groove", padx=5, pady=10, font=("Arial", 18)).place(x=20, y=70 * k)
                    # tk.Label(self.Result_, text="N/A", borderwidth=3, relief="groove", padx=5, pady=10,font=("Arial", 18),fg='#A3A6AB').place(x=35, y=70*k)
                    # tk.Label(self.Score_Outline, text="", borderwidth=3, relief="groove", padx=55, pady=10,font=("Arial", 18)).place(x=2, y=70*k)
                    # tk.Label(self.Score_Area, text="", borderwidth=3, relief="groove", padx=55, pady=10,font=("Arial", 18)).place(x=2, y=70*k)
        except:
            pass

    def Camera(self):
        try:
            if Quantity_Cam == 1:
                self.Camopen1 = cv.cvtColor(frame0.read()[1], cv.COLOR_BGR2RGB)
                img = Image.fromarray(self.Camopen1)
                resize_img = img.resize((600, 420))
                imgtk = ImageTk.PhotoImage(image=resize_img)
                self.frame.imgtk = imgtk
                self.frame.configure(image=imgtk)
            elif Quantity_Cam == 2:
                self.Camopen1 = cv.cvtColor(frame0.read()[1], cv.COLOR_BGR2RGB)
                self.Camopen2 = cv.cvtColor(frame1.read()[1], cv.COLOR_BGR2RGB)
                if self.Label_cam['text'] == "Cam1":
                    img = Image.fromarray(self.Camopen1)
                    resize_img = img.resize((600, 420))
                elif self.Label_cam['text'] == "Cam2":
                    img = Image.fromarray(self.Camopen2)
                    resize_img = img.resize((600, 420))
                imgtk = ImageTk.PhotoImage(image=resize_img)
                self.frame.imgtk = imgtk
                self.frame.configure(image=imgtk)
            self.after(60, self.Camera)
        except:
            messagebox.showerror('Python Error', 'Check Cameras')

    def callback_cam(self):
        self.Label_cam.configure(text=self.cam.get())

        # def come(self):
        # print(self.callback_cam())
        # self.after(500, self.come)

    def combobox_cam(self):
        self.n = tk.StringVar()
        self.cam = ttk.Combobox(self, width=8, height=80, textvariable=self.n)
        self.cam.configure(font=("Arial", 20))
        self.cam.configure(justify="center", foreground="green")
        if Quantity_Cam == 1:
            self.cam['values'] = ('Cam1')
        elif Quantity_Cam == 2:
            self.cam['values'] = ('Cam1', 'Cam2')
        self.cam.current(0)
        self.cam.place(x=500, y=15)

    def ViewImage(self):
        if Quantity_Cam == 1:
            image1 = Image.open(r"Snap1.bmp")
            resize_img1 = image1.resize((540, 350))
            image_1 = ImageTk.PhotoImage(resize_img1)
            self.view1.image_1 = image_1
            self.view1.configure(image=image_1)
        elif Quantity_Cam == 2:
            image1 = Image.open(r"Snap1.bmp")
            image2 = Image.open(r"Snap2.bmp")
            resize_img1 = image1.resize((540, 350))
            resize_img2 = image2.resize((540, 350))
            image_1 = ImageTk.PhotoImage(resize_img1)
            self.view1.image_1 = image_1
            self.view1.configure(image=image_1)
            image_2 = ImageTk.PhotoImage(resize_img2)
            self.view2.image_1 = image_2
            self.view2.configure(image=image_2)

        # self.image_show_snap1 = tk.Label(image=image_1)
        # self.image_show_snap1.image = self.image_1
        # self.image_show_snap1.place(x=1280, y=45)

    def Alarm_continue(self):
        if not self.Speaker:
            mixer.init()
            mixer.music.load('Alarm.mp3')
            mixer.music.play()
        elif self.Speaker:
            mixer.stop()

    def Alarm(self, Result):
        mixer.init()
        mixer.music.load('Alarm.mp3')
        if not Result:
            self.Run_Alarm = InfiniteTimer(11, self.Alarm_continue)
            self.Run_Alarm.start()
            mixer.music.play()

    def Destroy(self):
        self.Alarm(True)
        self.Speaker = True
        response = messagebox.askquestion("Close Programe", "Are you sure?", icon='warning')
        if response == "yes":
            if Quantity_Cam == 1:
                frame0.release()
            elif Quantity_Cam == 2:
                frame0.release()
                frame1.release()
            cv.destroyAllWindows()
            #self.Run_Alarm.cancel()
            app.destroy()

    def Board_run(self):
        ClassBoard = Borad()
        Hex = ClassBoard.ReadBorad()[0]
        return [Hex]

    def CallKeyBorad(self):
        self.LabelKeyBorad = tk.Label(self)
        self.LabelKeyBorad.bind_all('<KeyRelease>', self.Processing)

    def Processing(self, event):
        # print(getattr(App, 'handle_tab_changed'))
        with open('Status .json', 'r') as json_file:
            Status = json.loads(json_file.read())
        Tab = Status[0]["Status"]
        if Tab == "Main":
            if self.count != 0:
                self.btn_reset.focus_set()
                if event.char == '5':
                    self.Close_Login = True
                    self.ProcessP.place_forget()
                    self.ProcessP = tk.Label(self.Process, text="Process")
                    self.ProcessP.configure(font=("Arial", 18))
                    self.ProcessP.configure(fg="#8B8B00")
                    self.ProcessP.place(x=10, y=15, anchor=tk.W)
                    self.SaveImage()
                    self.ViewImage()
                    self.Main()
                    self.ShowScore()
                    self.ShowResult()
                    self.Save_Image()
                    self.ProcessP.place_forget()
                    self.ProcessP = tk.Label(self.Process, text="Ready")
                    self.ProcessP.configure(font=("Arial", 18))
                    self.ProcessP.configure(fg="Green")
                    self.ProcessP.place(x=10, y=15, anchor=tk.W)

    """""
    def Board_show(self):
        self.Bit = self.Board_run()[0].split("#")
        self.Bit = bytes(self.Bit[1], "ascii")
        self.Bit = "{:08b}".format(int(self.Bit.hex(), 16))
        self.Board = tk.LabelFrame(self, text="I/O Board")
        self.Board.configure(font=("Arial", 13))
        self.Board.configure(fg='Green')
        self.Board.place(x=1075, y=70, height=60, width=120)
        self.BoardP = tk.Label(self.Board, text=self.Board_run()[0])
        if self.Bit == "110000001100010000110100001010":  # 01
            self.SaveImage()
            self.ViewImage()
            self.Main()
            self.ShowScore()
            self.ShowResult()
            self.Save_Image()
        self.BoardP.configure(font=("Arial", 13))
        self.BoardP.configure(fg='Green')
        self.BoardP.place(x=10, y=35, anchor=tk.W)
    """""

    def SaveImage(self):
        if Quantity_Cam == 1:
            self.Seve1 = cv.cvtColor(frame0.read()[1], cv.COLOR_BGR2RGB)
            self.PLTimg1 = Image.fromarray(self.Seve1)
            self.PLTimg1.save("Snap1.bmp")
        elif Quantity_Cam == 2:
            self.Seve1 = cv.cvtColor(frame0.read()[1], cv.COLOR_BGR2RGB)
            self.Seve2 = cv.cvtColor(frame1.read()[1], cv.COLOR_BGR2RGB)
            self.PLTimg1 = Image.fromarray(self.Seve1)
            self.PLTimg2 = Image.fromarray(self.Seve2)
            self.PLTimg1.save("Snap1.bmp")
            self.PLTimg2.save("Snap2.bmp")

    def Img_part(self):
        # PartImg = "IMG_PART" + "\\" + "" + self.Part_API + "" + ".png"
        try:
            image1 = Image.open(r"IMG_PART" + "\\" + "" + self.Part_API + "" + ".png")
            resize_img = image1.resize((600, 340))
            self.test = ImageTk.PhotoImage(resize_img)
            self.image_show = tk.Label(image=self.test)
            self.image_show.image = self.test
            self.image_show.place(x=615, y=250)
        except:
            pass
            # tk.messagebox.showwarning("Image Part", "No Image")

    def PrintText(self):
        with open('Couter_Printer.json', 'r') as json_file:
            Data = json.loads(json_file.read())
        Packing_Couter = Data["Couter"]
        PackPart = Data["Partnumber"]
        self.PACKING_NUMBER = tk.LabelFrame(self, text="PACKING")
        self.PACKING_NUMBER.configure(font=("Arial", 13))
        self.PACKING_NUMBER.configure(fg='Green')
        self.PACKING_NUMBER.place(x=615, y=150, height=60, width=120)
        self.PACKING_NUMBERP = tk.Label(self.PACKING_NUMBER, text=str(Packing_Couter) + "/" + str(self.Packing_API))
        self.PACKING_NUMBERP.configure(font=("Arial", 13))
        self.PACKING_NUMBERP.configure(fg='Green')
        self.PACKING_NUMBERP.place(x=10, y=15, anchor=tk.W)

    def Couter_Printer(self):
        with open('Couter_Printer.json', 'r') as json_file:
            Data = json.loads(json_file.read())
        Packing_Couter = Data["Couter"]
        PackPart = Data["Partnumber"]

        if PackPart != self.Part_API:
            Printer = {"Partnumber": self.Part_API, "Couter": 1, "Packing": self.Packing_API}
            with open('Couter_Printer.json', 'w') as json_file:
                json.dump(Printer, json_file, indent=6)
        else:
            Printer = {"Partnumber": self.Part_API, "Couter": Packing_Couter + 1, "Packing": self.Packing_API}
            with open('Couter_Printer.json', 'w') as json_file:
                json.dump(Printer, json_file, indent=6)

            if self.Packing_API == Packing_Couter:
                Printer = {"Partnumber": self.Part_API, "Couter": 1, "Packing": self.Packing_API}
                with open('Couter_Printer.json', 'w') as json_file:
                    json.dump(Printer, json_file, indent=6)
                with open('Printer.txt', 'w') as f:
                    f.write('Printer')

    def Process_Outline(self, imgframe, imgTemplate, Left, Top, Right, Bottom):
        img = cv.imread(imgframe, 0)
        template = cv.imread(imgTemplate, 0)
        w, h = template.shape[::-1]
        TemplateThreshold = 0.8
        curMaxVal = 0
        c = 0
        for meth in ['cv.TM_CCOEFF_NORMED']:
            method = eval(meth)
            try:
                crop_image_ = img[(Top - 30):(Bottom + 30), (Left - 30):(Right + 30)]
                res = cv.matchTemplate(crop_image_, template, method)
            except:
                crop_image = img[Top:Bottom, Left:Right]
                res = cv.matchTemplate(crop_image, template, method)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
            if max_val > TemplateThreshold and max_val > curMaxVal:
                curMaxVal = max_val
                curMaxTemplate = c
                curMaxLoc = max_loc
            c = c + 1

        try:
            if curMaxTemplate == -1:
                return (0, (0, 0), 0, 0, 0, 0)
            else:
                # print((curMaxTemplate % 3, curMaxLoc, 1 - int(curMaxTemplate / 3) * 0.2, curMaxVal, w, h))
                return (curMaxTemplate % 3, curMaxLoc, 1 - int(curMaxTemplate / 3) * 0.2, curMaxVal, w, h)
        except:
            return (0, (0, 0), 0, 0, 0, 0)

    def Crop_image_Area(self, imgframe, Left, Top, Right, Bottom):
        img = cv.imread(imgframe, 0)
        #ret2, ImageRealTime = cv.threshold(img, 100, 255, cv.THRESH_BINARY)
        crop_image = img[Top:Bottom, Left:Right]
        return crop_image

    def Rule_Of_Thirds(self, ROT):
        total = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        mod = len(ROT) % 9
        if mod != 0:
            for i in range(mod):
                total[9] += sum(ROT[len(ROT) - mod + i])
        layout = int(len(ROT) / 9)
        for i in range(9):
            i = i + 1
            for j in range(layout * i):
                total[i - 1] += sum(ROT[j])
        point = [total[0]]
        for k in range(8):
            point.append(total[k + 1] - total[k])
        if mod != 0:
            point.append(total[9])
        return point
    def Process_Area(self, Data1, Data2):
            Score_Ture = []
            Chack = []
            swapped = False
            Result_Score = 0
            for i in range(len(Data1)):
                total = (((Data1[i] + Data2[i]) / 2) / Data2[i])
                if total < 1.99:
                    score_out = int(total * 1000)
                    if score_out > 1000:
                        score_out = 1000 - (score_out - 1000)
                        Chack.append(1)
                    else:
                        Chack.append(0)
                    Score_Ture.append(score_out)
                else:
                    Score_Ture.append(0)
                    Chack.append(0)

            for n in range(len(Score_Ture) - 1, 0, -1):
                for i in range(n):
                    if Score_Ture[i] > Score_Ture[i + 1]:
                        swapped = True
                        Score_Ture[i], Score_Ture[i + 1] = Score_Ture[i + 1], Score_Ture[i]
            for i in range(len(Score_Ture)):
                if i <= 4:
                    Result_Score += Score_Ture[i]
            Result_Score = int(Result_Score/5)
            return [Result_Score, sum(Chack)]

    def Main(self):
        if self.count != 0:
            self.sts = []
            self.Color = []
            self.Color_Show = []
            self.ImageSave = []
            self.Result = []
            self.Score_Outline_Data = []
            self.Score_Area_Data = []
            self.padx = []
            self.place = []
            for x in range(self.count):
                if self.Point_Camera[x] == "Cam1":
                    image = r'Snap1.bmp'
                elif self.Point_Camera[x] == "Cam2":
                    image = r'Snap2.bmp'
                self.ImageSave.append(cv.imread(image))
                Template = r"" + self.Part_API + "\Master""\\""Point" + str(x + 1) + "_Template.bmp"
                (template, top_left, scale, val, w, h) = self.Process_Outline(image, Template, self.Point_Left[x], self.Point_Top[x], self.Point_Right[x], self.Point_Bottom[x])
                Template_View = cv.imread(Template, 0)
               #ret1, Template_View = cv.threshold(Template_View, 100, 255, cv.THRESH_BINARY)
                Master_Image = self.Crop_image_Area(image, self.Point_Left[x], self.Point_Top[x], self.Point_Right[x], self.Point_Bottom[x])
                (Score_Area_Data, Chack) = self.Process_Area(self.Rule_Of_Thirds(Master_Image), self.Rule_Of_Thirds(Template_View))
                self.Score_Outline_Data.append(int(round(val * 1000, 0)))
                self.Score_Area_Data.append(Score_Area_Data)
                if scale == 1 and (val * 1000) >= self.Point_Score_Outline[x] and Score_Area_Data >= self.Point_Score_Area[x]:
                    self.Result.append(1)
                    self.Color.append((0, 255, 0))
                    self.Color_Show.append("Green")
                    self.padx.append(35)
                else:
                    self.Result.append(0)
                    self.Color.append((0, 0, 255))
                    self.Color_Show.append("Red")
                    self.padx.append(35)
                self.place.append(x * 70)

    def ResultComfrim(self):
        if self.Comfrim_Data >= 4:
            self.NG_Data = self.NG_Data + 1
            self.Save_Score()
            self.Result_NG = tk.Label(self.NG, text=self.NG_Data, borderwidth=3, relief="ridge", padx=5, pady=10)
            self.Result_NG.configure(font=("Arial", 25))
            self.Result_NG.configure(fg='Red')
            self.Result_NG.place(x=15, y=0, height=70, width=200)




    def ShowResult(self):
        with open('Result.json', 'r') as json_file:
            json_object = json.loads(json_file.read())
            Result = json_object[0]["Result"]

        if self.count != 0:
            for i in range(len(self.Result)):
                if self.Result[i] == 1:
                    if i == len(self.Result) - 1:
                        if Result == 0:
                            self.Alarm(True)
                            self.Speaker = True
                            Save_Result(1)
                        self.Couter_Printer()
                        self.PrintText()
                        self.OK_Data = self.OK_Data + 1
                        self.Comfrim_Data = 0
                        self.Save_Score()
                        self.Result_Ok = tk.Label(self.OK, text=self.OK_Data, borderwidth=3, relief="ridge", padx=5, pady=10)
                        self.Result_Ok.configure(font=("Arial", 25))
                        self.Result_Ok.configure(fg='Green')
                        self.Result_Ok.place(x=15, y=0, height=70, width=200)
                        # ClassBoard = Borad()
                        # ClassBoard.inst.write("@1 R00")
                else:
                    if Result == 1:
                        self.Alarm(False)
                        self.Speaker = False
                        Save_Result(0)
                    self.Comfrim_Data = self.Comfrim_Data + 1
                    self.ResultComfrim()
                    break


    def ShowScore(self):
        if self.count != 0:
            for i in range(self.count):
                if self.Result[i] == 1:
                    tk.Label(self.Result_, text="OK", borderwidth=3, relief="groove", bg=self.Color_Show[i], font=("Arial", 18), padx=35, pady=8).place(x=2, y=self.place[i])
                else:
                    tk.Label(self.Result_, text="NG", borderwidth=3, relief="groove", bg=self.Color_Show[i], font=("Arial", 18), padx=35, pady=8).place(x=2, y=self.place[i])
                tk.Label(self.Score_Outline, text=str(self.Score_Outline_Data[i]), borderwidth=3, relief="groove", font=("Arial", 18), padx=self.padx[i], pady=8).place(x=2, y=self.place[i])
                tk.Label(self.Score_Area, text=str(self.Score_Area_Data[i]), borderwidth=3, relief="groove", font=("Arial", 18), padx=self.padx[i], pady=8).place(x=2, y=self.place[i])

    def Save_Image(self):
        named_tuple = time.localtime()
        Date = time.strftime("%Y%m%d",named_tuple)
        Time = time.strftime("%Y%m%d%H%M%S", named_tuple)

        for s in range(self.count):
            FileFolder_Ok = 'Record/'+Date+'/'+self.Part_API+'/OK'
            path = os.path.join(FileFolder_Ok)
            try:
                os.makedirs(path, exist_ok=True)
            except OSError as error:
                pass
            FileFolder_NG = 'Record/'+Date+'/'+self.Part_API+'/NG'
            path = os.path.join(FileFolder_NG)
            try:
                os.makedirs(path, exist_ok=True)
            except OSError as error:
                pass
            cv.rectangle(self.ImageSave[s], (self.Point_Left[s], self.Point_Top[s]), (self.Point_Right[s], self.Point_Bottom[s]), self.Color[s], 3)
            cv.putText(self.ImageSave[s], "Score Outline : " + str(self.Score_Outline_Data[s]) + " / " + str(self.Point_Score_Outline[s]), (10, 25), cv.FONT_HERSHEY_SIMPLEX, 1, self.Color[s], 2)
            cv.putText(self.ImageSave[s], "Score Area : " + str(self.Score_Area_Data[s]) + " / " + str(self.Point_Score_Area[s]), (10, 55), cv.FONT_HERSHEY_SIMPLEX, 1, self.Color[s], 2)
            cv.putText(self.ImageSave[s], "Time : " + str(Time) + "", (10, 85), cv.FONT_HERSHEY_SIMPLEX, 1, self.Color[s], 2)
            if self.Result[s] == 1:
            # cv.imwrite('Record/' + self.Part_API + '/' + self.Result[s] + '/Point' + str(s + 1) + '/' + time_string + '_P0' + str(s + 1) + '.png', self.ImageSave[s])
                cv.imwrite('Record/'+Date+'/'+self.Part_API+ '/OK/' + Time + '_P0' + str(s + 1) + '.jpg', self.ImageSave[s])
            else:
                cv.imwrite('Record/'+Date+'/'+self.Part_API+ '/NG/' + Time + '_P0' + str(s + 1) + '.jpg', self.ImageSave[s])

    def Save_Score(self):
        named_tuple = time.localtime()
        #Time = time.strftime("%Y-%m-%d_%H%M%S", named_tuple)
        Time = time.strftime("%Y%m%d%H%M%S", named_tuple)
        parent_dir = 'Transaction/'
        path = os.path.join(parent_dir)
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as error:
            pass
        Transition = [dict(PartNumber=self.Part_API, BatchNumber=self.Batch_API, MachineName=self.Machine_API, Details=[])]
        for s in range(self.count):
            Transition[0]["Details"].append([dict(Score=int(self.Score_Area_Data[s]),
                                                  Result=self.Result[s], Point=s + 1)])
        with open('Transaction/' + Time + '.json', 'w') as json_file:
            json.dump(Transition, json_file, indent=6)


class Frame2(ttk.Frame, App):
    def __init__(self, container):
        super().__init__()
        self.Label_cam = tk.Label(self, text="Cam1")
        self.frame = tk.Label(self)
        self.frame.place(x=5, y=70)
        self.Camera()
        self.combobox_cam()
        self.combobox_Point()
        self.Score_Outline()
        self.Score_Area()
        self.CallPart()
        self.Close_()

        self.btn_cam = tk.Button(self, text="Choose Camera", command=self.callback_cam)
        self.btn_cam.configure(font=("Arial", 13))
        self.btn_cam.configure(justify="center", foreground="green")
        self.btn_cam.place(x=1200, y=72)

        # Login
        self.Password = tk.StringVar()  # string variable
        self.BoxPassword = tk.Entry(self, font="Arial", show='*', textvariable=self.Password)
        self.BoxPassword.configure(font=("Arial", 20))
        self.BoxPassword.place(x=1350, y=70, width=250, height=35)

        def character_limit(Password):
            try:
                if len(Password.get()) > 0:
                    Password.set(Password.get()[6])
            except:
                pass

        self.Password.trace("w", lambda *args: character_limit(self.Password))
        self.chack_Value_Password = tk.IntVar(value=0)

        def Show_Password():
            if (self.chack_Value_Password.get() == 1):
                self.BoxPassword.config(show='')
            else:
                self.BoxPassword.config(show='*')

        self.show_password = tk.Checkbutton(self, text='Show Password', variable=self.chack_Value_Password,
                                            onvalue=1, offvalue=0, command=Show_Password)
        self.show_password.place(x=1350, y=110)

        self.buttonLogin = tk.Button(self, text="Login", command=self.Search)
        self.buttonLogin.configure(font=("Arial", 13))
        self.buttonLogin.configure(justify="center", foreground="green")
        self.buttonLogin.place(x=1620, y=70)

        self.message = tk.StringVar()
        self.show_message = tk.Label(self, text="", textvariable=self.message)
        self.show_message.configure(font=("Arial", 13))
        self.show_message.place(x=1350, y=40)

        self.messageAdd = tk.StringVar()
        self.show_messageAdd = tk.Label(self, text="", textvariable=self.messageAdd)
        self.show_messageAdd.configure(font=("Arial", 13))
        self.show_messageAdd.place(x=1050, y=330)

        # self.image1 = Image.open(r"Snap1.jpg")
        # self.tkimage = ImageTk.PhotoImage(self.image1)

    def Close_(self):
        with open('Status .json', 'r') as json_file:
            Status = json.loads(json_file.read())
        Tab = Status[0]["Status"]
        if Tab == "Main":
            try:
                self.callLogin()
            except:
                pass
        self.after(300000, self.Close_)

    def CallPart(self):
        self.API_json = Getpart()
        self.API_json.__int__()
        self.Part_API = self.API_json.Get()[0]
        self.Batch_API = self.API_json.Get()[1]
        self.Machine_API = self.API_json.Get()[4]

        self.Machine_Vision = tk.Label(self, text='Machine Vision Inspection')
        self.Machine_Vision.configure(font=("Arial", 30))
        self.Machine_Vision.configure(fg=('Green'))
        self.Machine_Vision.place(x=15, y=5)

        self.PART = tk.LabelFrame(self, text="PART NUMBER")
        self.PART.configure(font=("Arial", 13))
        self.PART.configure(fg='Green')
        self.PART.place(x=1050, y=150, height=60, width=180)
        self.PARTP = tk.Label(self.PART, text=self.Part_API)
        self.PARTP.configure(font=("Arial", 13))
        self.PARTP.configure(fg='Green')
        self.PARTP.place(x=10, y=15, anchor=tk.W)

    def Loginform(self):
        self.Emp_ID = self.Password.get()
        with open('Information\Operator.json', 'r') as json_Part:
            json_object = json.loads(json_Part.read())
            id_Emp = []
            for d in json_object:
                id_Emp.append(d['id_Emp'])
        for i in range(len(id_Emp)):
            if id_Emp[i] == self.Emp_ID:
                return True
        return False

    def Search(self):
        if self.Loginform():
            self.CallPart()
            self.message.set("Login success")
            self.show_message.configure(fg="green")
            self.ADD = tk.Button(self, text="Add", command=self.CallImage)
            self.ADD.configure(font=("Arial", 25))
            self.ADD.configure(fg="Green")
            self.ADD.place(x=1050, y=620)
            self.buttonLogin.place_forget()

            self.buttonLogout = tk.Button(self, text="Logout", command=self.callLogin)
            self.buttonLogout.configure(font=("Arial", 13))
            self.buttonLogout.configure(justify="center", foreground="red")
            self.buttonLogout.place(x=1620, y=70)
        else:
            self.message.set("Wrong password did not match")
            self.show_message.configure(fg="Red")

    def callLogin(self):
        self.message.set("")
        self.BoxPassword.delete(0, 6)
        self.buttonLogout.place_forget()
        self.ADD.place_forget()
        self.buttonLogin = tk.Button(self, text="Login", command=self.Search)
        self.buttonLogin.configure(font=("Arial", 13))
        self.buttonLogin.configure(justify="center", foreground="green")
        self.buttonLogin.place(x=1620, y=70)

    # ADD
    def CallImage(self):
        Emp_ID = self.Password.get()
        Score_Outline = self.Score_Data_Outline.get()
        Score_Area = self.Score_Data_Area.get()
        Cam = self.cam.get()
        Point = self.Point_value.get()
        if str.isdigit(Score_Outline) and str.isdigit(Score_Area):
            if int(Score_Outline) >= 500 and int(Score_Area) >= 550:
                self.messageAdd.set("")
                if Cam == "Cam1":
                    self.path = cv.cvtColor(frame0.read()[1], cv.COLOR_BGR2RGB)
                elif Cam == "Cam2":
                    self.path = cv.cvtColor(frame1.read()[1], cv.COLOR_BGR2RGB)
                self.PLTimg1 = Image.fromarray(self.path)
                self.PLTimg1.save("Current.bmp")
                Create = '' + self.Part_API + '/Master'
                if not os.path.exists(Create):
                    os.makedirs(Create)
                    # print("Directory ", Create, " Created ")
                else:
                    print("")
                refPt = []
                cropping = False

                def click_and_crop(event, x, y, flags, param):
                    global refPt, cropping
                    image = clone.copy()

                    if event == cv.EVENT_LBUTTONDOWN:
                        refPt = [(x, y)]
                        # print(refPt)
                        cropping = True
                    elif event == cv.EVENT_LBUTTONUP:
                        refPt.append((x, y))
                        # print(refPt)
                        cropping = False
                        cv.rectangle(image, refPt[0], refPt[1], (85, 255, 51), 2)
                        cv.imshow(Point, image)
                        if len(refPt) == 2:
                            roi = clone[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
                            x = cv.cvtColor(roi, cv.COLOR_BGR2RGB)
                            Left = refPt[0][0]
                            Top = refPt[0][1]
                            Right = refPt[1][0]
                            Bottom = refPt[1][1]
                            img = Image.fromarray(x)
                            Showtext = cv.putText(image, "Save image " + Point + "", (10, 25),
                                                  cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)
                            cv.imshow(Point, Showtext)
                            img.save('' + Create + '/' + Point + '_Template.bmp')

                            if Left and Top and Right and Bottom != 0:
                                self.Master(Left, Top, Right, Bottom, Score_Outline, Score_Area, Cam, Point, Emp_ID)

                path = r'Current.bmp'
                image = cv.imread(path)

                clone = image.copy()
                cv.namedWindow(Point)
                cv.setMouseCallback(Point, click_and_crop)
                cv.imshow(Point, image)
            else:
                self.messageAdd.set("Maximum Area Score 500")
                self.show_messageAdd.configure(fg="Red")
                # print("Maximum Area Score 500")
        else:
            self.messageAdd.set("Please enter a number")
            self.show_messageAdd.configure(fg="Red")
            # print("Please enter a number")

    def Master(self, Left, Top, Right, Bottom, Score_Outline, Score_Area, Cam, Point, Emp_ID):
        Score_Outline = int(Score_Outline)
        Score_Area = int(Score_Area)
        try:
            with open('Master_' + self.Part_API + '.json', 'r') as json_file:
                item = json.loads(json_file.read())
                for i in range(11):
                    str_ = str(i)
                    try:
                        if Point == "Point" + str_:
                            i = i - 1
                            item[i]["Point" + str_][0]["Emp ID"] = Emp_ID
                            item[i]["Point" + str_][0]["Camera"] = Cam
                            item[i]["Point" + str_][0]["Left"] = Left
                            item[i]["Point" + str_][0]["Top"] = Top
                            item[i]["Point" + str_][0]["Right"] = Right
                            item[i]["Point" + str_][0]["Bottom"] = Bottom
                            item[i]["Point" + str_][0]["Score Outline"] = Score_Outline
                            item[i]["Point" + str_][0]["Score Area"] = Score_Area
                            with open('Master_' + self.Part_API + '.json', 'w') as json_file:
                                json.dump(item, json_file, indent=6)
                    except:
                        # item.append({''+Point+'': [{"Camera": "",'Left': "",'Top': "","Rigth": "","Bottom": "",'Score': ""}]}
                        with open('Master_' + self.Part_API + '.json', 'r') as json_file:
                            item = json.loads(json_file.read())
                        try:
                            logging.debug(item[i - 1])
                            item.append({'' + Point + '': [
                                {"Emp ID": Emp_ID, "Camera": Cam, 'Left': Left, 'Top': Top, "Right": Right, "Bottom": Bottom,
                                 'Score Outline': Score_Outline, 'Score Area': Score_Area}]})
                            with open('Master_' + self.Part_API + '.json', 'w') as json_file:
                                json.dump(item, json_file, indent=6)
                        except:
                            pass
        except FileNotFoundError as exc:
            if Point == "Point1":
                item = [
                    {'' + Point + '': [
                        {"Emp ID": Emp_ID, "Camera": Cam, 'Left': Left, 'Top': Top, "Right": Right, "Bottom": Bottom, 'Score Outline': Score_Outline, 'Score Area': Score_Area}]}]
                with open('Master_' + self.Part_API + '.json', 'w') as json_file:
                    json.dump(item, json_file, indent=6)

    def callback_cam(self):
        self.Label_cam.configure(text=self.cam.get())

    def combobox_cam(self):
        self.n = tk.StringVar()
        self.cam = ttk.Combobox(self, width=8, height=80, textvariable=self.n)
        self.cam.configure(font=("Arial", 20))
        self.cam.configure(justify="center", foreground="green")
        if Quantity_Cam == 1:
            self.cam['values'] = ('Cam1')
        elif Quantity_Cam == 2:
            self.cam['values'] = ('Cam1', 'Cam2')
        self.cam.current(0)
        self.cam.place(x=1050, y=70)

    def Camera(self):
        try:
            if Quantity_Cam == 1:
                self.Camopen1 = cv.cvtColor(frame0.read()[1], cv.COLOR_BGR2RGB)
                img = Image.fromarray(self.Camopen1)
                resize_img = img.resize((1000, 800))
                imgtk = ImageTk.PhotoImage(image=resize_img)
                self.frame.imgtk = imgtk
                self.frame.configure(image=imgtk)
            elif Quantity_Cam == 2:
                self.Camopen1 = cv.cvtColor(frame0.read()[1], cv.COLOR_BGR2RGB)
                self.Camopen2 = cv.cvtColor(frame1.read()[1], cv.COLOR_BGR2RGB)
                if self.Label_cam['text'] == "Cam1":
                    img = Image.fromarray(self.Camopen1)
                elif self.Label_cam['text'] == "Cam2":
                    img = Image.fromarray(self.Camopen2)
                img = img.resize((1000, 800))
                imgtk = ImageTk.PhotoImage(image=img)
                self.frame.imgtk = imgtk
                self.frame.configure(image=imgtk)
            self.after(40, self.Camera)
        except:
            messagebox.showerror('Python Error', 'Check Cameras')

    def combobox_Point(self):
        self.Point = tk.LabelFrame(self, text="Point")
        self.Point.configure(font=("Arial", 13))
        self.Point.configure(fg='Green')
        self.Point.place(x=1050, y=240, height=90, width=180)
        self.Point_value = tk.StringVar()
        self.Point_show = ttk.Combobox(self.Point, width=8, height=80, textvariable=self.Point_value)
        self.Point_show.configure(font=("Arial", 20))
        self.Point_show.configure(justify="center", foreground="green")
        self.Point_show['values'] = (
            'Point1', 'Point2', 'Point3', 'Point4', 'Point5', 'Point6', 'Point7', 'Point8', 'Point9', 'Point10')
        self.Point_show.current(0)
        self.Point_show.place(x=10, y=10)

    def Score_Outline(self):
        self.Score_Data_Outline = tk.StringVar()
        self.Score = tk.LabelFrame(self, text="Score Outline")
        self.Score.configure(font=("Arial", 13))
        self.Score.configure(fg='Green')
        self.Score.place(x=1050, y=360, height=90, width=330)
        self.Score_Show = tk.Entry(self.Score, font="Arial", textvariable=self.Score_Data_Outline)
        self.Score_Show.configure(font=("Arial", 20))
        self.Score_Show.configure(fg='Green')
        self.Score_Show.place(x=10, y=10)

        # self.len_score = str(self.Score_Data.get())
        def score_limit(*args):
            s = self.Score_Data_Outline.get()
            if str.isdigit(s):
                if len(s) > 3:
                    self.Score_Data_Outline.set(s[:3])
            else:
                self.Score_Data_Outline.set(s[:0])

        self.Score_Data_Outline.trace("w", score_limit)

    def Score_Area(self):
        self.Score_Data_Area = tk.StringVar()
        self.Score_Area = tk.LabelFrame(self, text="Score Area")
        self.Score_Area.configure(font=("Arial", 13))
        self.Score_Area.configure(fg='Green')
        self.Score_Area.place(x=1050, y=480, height=90, width=330)
        self.Score_Show_Area = tk.Entry(self.Score_Area, font="Arial", textvariable=self.Score_Data_Area)
        self.Score_Show_Area.configure(font=("Arial", 20))
        self.Score_Show_Area.configure(fg='Green')
        self.Score_Show_Area.place(x=10, y=10)

        # self.len_score = str(self.Score_Data.get())
        def score_limit(*args):
            s = self.Score_Data_Area.get()
            if str.isdigit(s):
                if len(s) > 3:
                    self.Score_Data_Area.set(s[:3])
            else:
                self.Score_Data_Area.set(s[:0])

        self.Score_Data_Area.trace("w", score_limit)


if __name__ == "__main__":
    app = App()
    app.mainloop()
    # messagebox.showerror('Python Error', 'Error Programe')