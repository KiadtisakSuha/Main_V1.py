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
import subprocess


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

elif Quantity_Cam == 3:
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

    frame3 = cv.VideoCapture(2, cv.CAP_DSHOW)
    frame3.set(cv.CAP_PROP_FRAME_WIDTH, 1024)
    frame3.set(cv.CAP_PROP_FRAME_HEIGHT, 768)
    frame3.set(cv.CAP_PROP_AUTO_EXPOSURE, 0)
    frame3.set(cv.CAP_PROP_AUTOFOCUS, 0)
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

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        ttk.Style().configure('TNotebook.Tab', font=('Arial', 20),
                              background='black', foreground='#006400', borderwidth=0)
        self.title('Machine Vision Inspection 1.0.5')
        self.geometry("1920x1020+0+0")
        #self.state('zoomed')
        #self.attributes('-fullscreen', True)
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

        self.Batch_API = self.API_json.Get()[1]
        self.Batch_API_Get = self.Batch_API
        self.Machine_Vision = tk.Label(self, text='Machine Vision Inspection')
        self.Machine_Vision.configure(font=("Arial", 30))
        self.Machine_Vision.configure(fg=('Green'))
        self.Machine_Vision.place(x=15, y=5)

        self.Machine_Version = tk.Label(self, text='v1.0.5')
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




if __name__ == "__main__":
    app = App()
    app.mainloop()