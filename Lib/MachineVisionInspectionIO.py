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
import numpy as np

with open('Setting Paramiter.json', 'r') as json_file:
    Setting_Paramiter = json.loads(json_file.read())
Quantity_Cam = Setting_Paramiter[0]["Quantity_Cam"]
Board_Name = Setting_Paramiter[0]["Board_Name"]
Machine = Setting_Paramiter[0]["MachineName"]
Mode = Setting_Paramiter[0]["Mode"]

"""frame0.set(cv.CAP_PROP_FRAME_WIDTH, 1024)
frame0.set(cv.CAP_PROP_FRAME_HEIGHT, 768)
frame0.set(cv.CAP_PROP_AUTO_EXPOSURE, 0)
frame0.set(cv.CAP_PROP_AUTOFOCUS, 0)"""

if Quantity_Cam == 1:
    frame0 = cv.VideoCapture(0, cv.CAP_DSHOW)
    frame0.set(cv.CAP_PROP_FRAME_WIDTH, 1980)
    frame0.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
    frame0.set(cv.CAP_PROP_AUTO_EXPOSURE, 0)
    frame0.set(cv.CAP_PROP_AUTOFOCUS, 0)
elif Quantity_Cam == 2:
    frame0 = cv.VideoCapture(0, cv.CAP_DSHOW)
    frame0.set(cv.CAP_PROP_FRAME_WIDTH, 1980)
    frame0.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
    frame0.set(cv.CAP_PROP_AUTO_EXPOSURE, 0)
    frame0.set(cv.CAP_PROP_AUTOFOCUS, 0)
    frame1 = cv.VideoCapture(1, cv.CAP_DSHOW)
    frame1.set(cv.CAP_PROP_FRAME_WIDTH, 1980)
    frame1.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
    frame1.set(cv.CAP_PROP_AUTO_EXPOSURE, 0)
    frame1.set(cv.CAP_PROP_AUTOFOCUS, 0)

elif Quantity_Cam == 3:
    frame0 = cv.VideoCapture(0, cv.CAP_DSHOW)
    frame0.set(cv.CAP_PROP_FRAME_WIDTH, 1980)
    frame0.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
    frame0.set(cv.CAP_PROP_AUTO_EXPOSURE, 0)
    frame0.set(cv.CAP_PROP_AUTOFOCUS, 0)

    frame1 = cv.VideoCapture(1, cv.CAP_DSHOW)
    frame1.set(cv.CAP_PROP_FRAME_WIDTH, 1980)
    frame1.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
    frame1.set(cv.CAP_PROP_AUTO_EXPOSURE, 0)
    frame1.set(cv.CAP_PROP_AUTOFOCUS, 0)

    frame2 = cv.VideoCapture(2, cv.CAP_DSHOW)
    frame2.set(cv.CAP_PROP_FRAME_WIDTH, 1980)
    frame2.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
    frame2.set(cv.CAP_PROP_AUTO_EXPOSURE, 0)
    frame2.set(cv.CAP_PROP_AUTOFOCUS, 0)

font = cv.FONT_HERSHEY_SIMPLEX

"""
def Save_Result(Data):
    item = [{'Result': Data}]
    with open('Result.json', 'w') as json_file:
        json.dump(item, json_file)"""

class Getpart():
    def __init__(self):
        self.Sever = None

    def __int__(self):
        # with open('GetPart_API.txt', 'r') as API_Part:
        # self.Part_Paramiter = API_Part.read()
        self.Part_Paramiter = "http://192.168.1.48:89/RobotAPI/GetPart?machineId=" + Machine + ""

    def Get(self):
        try:
            with urllib.request.urlopen(self.Part_Paramiter, timeout=3) as response:
                json_API = json.loads(response.read())
            self.Sever = "Connected"
            self.PartNumber = json_API[0]["PartNumber"]
            self.BatchNumber = json_API[0]["BatchNumber"]
            self.PartName = json_API[0]["PartName"]
            self.CustomerPartNumber = json_API[0]["CustomerPartNumber"]
            self.MachineName = json_API[0]["MachineName"]
            self.MoldId = json_API[0]["MoldId"]
            self.Packing = json_API[0]["PackingStd"]
            with open('Planning Data.json', 'w') as Keep_Part:
                json.dump(json_API, Keep_Part, indent=6)
        except:
            with open('Planning Data.json', 'r') as json_Part:
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

class GetEmp:
    @staticmethod
    def Information():
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
        return [self.Read_Board, self.inst.write, self.data]


class InfiniteTimer():
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
        if self._should_continue:
            self.thread = Timer(self.seconds, self._handle_target)
            self.thread.start()

    def start(self):
        if not self._should_continue and not self.is_running:
            self._should_continue = True
            self._start_timer()
        else:
            pass

    def cancel(self):
        if self.thread is not None:
            self._should_continue = False
            self.thread.cancel()
        else:
            pass

class Save_Data:
    @staticmethod
    def Save_Imaga_Run(Camera1,Camera2,Camera3):
            if Quantity_Cam >= 1:
                Save_Image_1 = Image.fromarray(Camera1)
                Save_Image_1.save("Snap1.bmp")
                if Quantity_Cam >= 2:
                    Save_Image_2 = Image.fromarray(Camera2)
                    Save_Image_2.save("Snap2.bmp")
                    if Quantity_Cam >= 3:
                        Save_Image_3 = Image.fromarray(Camera3)
                        Save_Image_3.save("Snap3.bmp")

    @staticmethod
    def Save_Image(Partnumber,Counter,Image,Left,Top,Right,Bottom,Left_Find,Top_Find,Right_Find,Bottom_Find,Color,Outline_Score,Outline_Score_Set,Area_Score,Area_set_Score,Result,ROI):
        named_tuple = time.localtime()
        Time = time.strftime("%Y%m%d%H%M%S", named_tuple)
        for s in range(Counter):
                FileFolder_Ok = 'Record/' + Partnumber + '/OK/Point' + str(s + 1)
                path = os.path.join(FileFolder_Ok)
                try:
                    os.makedirs(path, exist_ok=True)
                except OSError as error:
                    pass
                FileFolder_NG = 'Record/' + Partnumber + '/NG/Point' + str(s + 1)
                path = os.path.join(FileFolder_NG)
                try:
                    os.makedirs(path, exist_ok=True)
                except OSError as error:
                    pass
                cv.rectangle(Image[s], (Left_Find[s], Top_Find[s]), (Right_Find[s], Bottom_Find[s]), Color[s], 2)
                cv.rectangle(Image[s], (Left[s]-ROI, Top[s]-ROI), (Right[s]+ROI, Bottom[s]+ROI), Color[s], 3)
                cv.putText(Image[s], "Score Outline : " + str(Outline_Score[s]) + " / " + str(Outline_Score_Set[s]), (10, 55), cv.FONT_HERSHEY_SIMPLEX, 1, Color[s], 2)
                cv.putText(Image[s], "Score Area : " + str(Area_Score[s]) + " / " + str(Area_set_Score[s]), (10, 85), cv.FONT_HERSHEY_SIMPLEX, 1, Color[s], 2)
                cv.putText(Image[s], "Time : " + str(Time) + "", (10, 115), cv.FONT_HERSHEY_SIMPLEX, 1, Color[s], 2)
                if s <= 8:
                    Point = "0"
                else:
                    Point = ""
                if Result[s] == 1:
                    cv.imwrite('Record/' + Partnumber +'/OK/Point' + str(s + 1)+'/'+Time + '_P' + Point + str(s + 1) + '.jpg', Image[s])
                else:
                    cv.imwrite('Record/' + Partnumber +'/NG/Point' + str(s + 1)+'/'+Time + '_P' + Point + str(s + 1) + '.jpg', Image[s])

    @staticmethod
    def Save_Score(Partnumber, Batch, Machine, Couter, Score, Result):
        named_tuple = time.localtime()
        Time = time.strftime("%Y%m%d%H%M%S", named_tuple)
        parent_dir = 'Transaction/'
        path = os.path.join(parent_dir)
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as error:
            pass
        Transition = [dict(PartNumber=Partnumber, BatchNumber=Batch, MachineName=Machine, Details=[])]
        for s in range(Couter):
            Transition[0]["Details"].append([dict(Score=int(Score[s]),
                                                  Result=Result[s], Point=s + 1)])
        with open('Transaction/' + Time + '.json', 'w') as json_file:
            json.dump(Transition, json_file, indent=6)

    @staticmethod


    def Master(Left, Top, Right, Bottom, Score_Outline,Score_Area,Cam,Point, Emp_ID, Partnumber):
            Score_Outline = int(Score_Outline)
            Score_Area = int(Score_Area)
            try:
                with open(Partnumber + '/' + Partnumber + '.json', 'r') as json_file:
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
                                with open(Partnumber + '/' + Partnumber + '.json', 'w') as json_file:
                                    json.dump(item, json_file, indent=6)
                        except:
                            # item.append({''+Point+'': [{"Camera": "",'Left': "",'Top': "","Rigth": "","Bottom": "",'Score': ""}]}
                            with open(Partnumber + '/' + Partnumber + '.json', 'r') as json_file:
                                item = json.loads(json_file.read())
                            try:
                                logging.debug(item[i - 1])
                                item.append({'' + Point + '': [
                                    {"Emp ID": Emp_ID, "Camera": Cam, 'Left': Left, 'Top': Top, "Right": Right, "Bottom": Bottom,
                                     'Score Outline': Score_Outline, 'Score Area': Score_Area}]})
                                with open(Partnumber + '/' + Partnumber + '.json', 'w') as json_file:
                                    json.dump(item, json_file, indent=6)
                            except:
                                pass
            except FileNotFoundError as exc:
                if Point == "Point1":
                    item = [
                        {'' + Point + '': [
                            {"Emp ID": Emp_ID, "Camera": Cam, 'Left': Left, 'Top': Top, "Right": Right, "Bottom": Bottom, 'Score Outline': Score_Outline, 'Score Area': Score_Area}]}]
                    with open(Partnumber + '/' + Partnumber+ '.json', 'w') as json_file:
                        json.dump(item, json_file, indent=6)



class App(tk.Tk):
    def __init__(self):
        GetEmp.Information()
        super().__init__()
        combostyle = ttk.Style()

        combostyle.theme_create('combostyle', parent='alt',
                                settings={'TCombobox':
                                              {'configure':
                                                   {'selectbackground': 'blue',
                                                    'fieldbackground': 'black',
                                                    'background': 'green'
                                                    }}}
                                )
        combostyle.theme_use('combostyle')
        ttk.Style().configure('TNotebook.Tab', font=('Arial', 20),
                              background='black', foreground='#006400', borderwidth=0)
        self.title('Machine Vision Inspection')

        self.geometry("1920x1020+0+0")
        self.overrideredirect(1)
        #self.state('zoomed')
        #self.protocol("WM_DELETE_WINDOW", self.Destroy)
        #self.attributes('-toolwindow', False)
        #self.attributes('-fullscreen', True)
        #self.resizable(0,0)
        self.configure(background='black')
        self.API_json = Getpart()
        self.Run_Camera_1 = None
        self.Run_Camera_2 = None
        self.Run_Camera_3 = None
        self.Close_Camera = False
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


        self.Machine_Vision = tk.Label(self, text='Machine Vision Inspection '+self.Machine_API,bg='black')
        self.Machine_Version = tk.Label(self, text='v1.0.1',bg='black')
        if self.Sever_API == "Connected":
            self.Machine_Vision.configure(fg='Green')
            self.Machine_Version.configure(fg='Green')
        else:
            self.Machine_Vision.configure(fg='Red')
            self.Machine_Version.configure(fg='Red')
        self.Machine_Vision.configure(font=("Arial", 25))
        self.Machine_Vision.place(x=15, y=5)
        self.Machine_Version.configure(font=("Arial", 10))
        self.Machine_Version.place(x=400, y=45)

        self.PART = tk.LabelFrame(self, text="BKF PART NUMBER",bg='black')
        self.PART.configure(font=("Arial", 10,'bold'))
        self.PART.configure(fg='Green')
        self.PART.place(x=395, y=70, height=60, width=150)
        self.PARTP = tk.Label(self.PART, text=self.Part_API,bg='black')
        self.PARTP.configure(font=("Arial", 13))
        self.PARTP.configure(fg='Green')
        self.PARTP.place(x=10, y=15, anchor=tk.W)

        self.PART_NAME = tk.LabelFrame(self, text="PART NAME",bg='black')
        self.PART_NAME.configure(font=("Arial", 10,'bold'))
        self.PART_NAME.configure(fg='Green')
        self.PART_NAME.place(x=555, y=70, height=60, width=390)
        self.PART_NAMEP = tk.Label(self.PART_NAME, text=self.part_name_API,bg='black')
        self.PART_NAMEP.configure(font=("Arial", 13))
        self.PART_NAMEP.configure(fg='Green')
        self.PART_NAMEP.place(x=10, y=15, anchor=tk.W)

        self.CUSTOMER_NUMBER = tk.LabelFrame(self, text="CUSTOMER NUMBER",bg='black')
        self.CUSTOMER_NUMBER.configure(font=("Arial", 10))
        self.CUSTOMER_NUMBER.configure(fg='Green')
        self.CUSTOMER_NUMBER.place(x=395, y=150, height=60, width=150)
        self.CUSTOMER_NUMBERP = tk.Label(self.CUSTOMER_NUMBER, text=self.Customer_API,bg='black')
        self.CUSTOMER_NUMBERP.configure(font=("Arial", 13))
        self.CUSTOMER_NUMBERP.configure(fg='Green')
        self.CUSTOMER_NUMBERP.place(x=10, y=15, anchor=tk.W)

        self.BATCH_NUMBER = tk.LabelFrame(self, text="BATCH NUMBER",bg='black')
        self.BATCH_NUMBER.configure(font=("Arial", 10))
        self.BATCH_NUMBER.configure(fg='Green')
        self.BATCH_NUMBER.place(x=555, y=150, height=60, width=150)
        self.BATCH_NUMBERP = tk.Label(self.BATCH_NUMBER, text=self.Batch_API,bg='black')
        self.BATCH_NUMBERP.configure(font=("Arial", 13))
        self.BATCH_NUMBERP.configure(fg='Green')
        self.BATCH_NUMBERP.place(x=10, y=15, anchor=tk.W)

        self.MOLD_NUMBER = tk.LabelFrame(self, text="MOLD NUMBER",bg='black')
        self.MOLD_NUMBER.configure(font=("Arial", 10))
        self.MOLD_NUMBER.configure(fg='Green')
        self.MOLD_NUMBER.place(x=720, y=150, height=60, width=225)
        self.MOLD_NUMBERP = tk.Label(self.MOLD_NUMBER, text=self.Mode_API,bg='black')
        self.MOLD_NUMBERP.configure(font=("Arial", 13))
        self.MOLD_NUMBERP.configure(fg='Green')
        self.MOLD_NUMBERP.place(x=10, y=15, anchor=tk.W)


        self.OK_Data = 0
        self.NG_Data = 0
        self.Comfrim_Data = 0
        self.Comfrim_SaveScore = 0
        #tk.Label(self,text="OK : ",font=("Arial", 50,'bold'),fg='Green').place(x=10, y=50)
        self.Result_Ok = tk.Label(self, text="OK : "+str(self.OK_Data),borderwidth=3, relief="ridge", padx=5, pady=10,bg='black')
        self.Result_Ok.configure(font=("Arial", 50,'bold'))
        self.Result_Ok.configure(fg='Green')
        self.Result_Ok.place(x=5, y=50 ,width=375)

        self.Result_NG = tk.Label(self, text="OK : "+str(self.OK_Data), borderwidth=3, relief="ridge", padx=5, pady=10,bg='black')
        self.Result_NG.configure(font=("Arial", 50,'bold'))
        self.Result_NG.configure(fg='Red')
        self.Result_NG.place(x=5, y=180,width=375)

        self.Label_cam = tk.Label(self, text="Cam1")
        self.frame = tk.Label(self,bg="black")
        self.frame.place(x=395, y=650)



        self.Process = tk.LabelFrame(self, text="Process",bg='black')
        self.Process.configure(font=("Arial", 10))
        self.Process.configure(fg='Green')
        self.Process.place(x=395, y=220, height=60, width=150)
        self.ProcessP = tk.Label(self.Process, text="Ready",fg='green',bg="black")
        self.ProcessP.configure(font=("Arial", 20))
        self.ProcessP.place(x=10, y=15, anchor=tk.W)

        #self.btn_Start = tk.Button(self,text="Start",command=self.Strat)
        #self.btn_Start.configure(font=("Arial", 18))
        #self.btn_Start.configure(fg='Yellow',bg="black")
        #self.btn_Start.place(x=1260, y=10, width=120)
        self.IMAGE()
        self.Call_IMAGE()
        self.combobox_cam()
        self.Camera()
        self.Printer()
        self.PrintText()

        self.Board = tk.LabelFrame(self, text="I/O Board",bg='black')
        self.Board.configure(font=("Arial", 10))
        self.Board.configure(fg='Green')
        self.Board.place(x=555, y=220, height=60, width=150)
        self.BoardP = tk.Label(self.Board,bg='black')
        self.BoardP.configure(font=("Arial", 13))
        self.BoardP.configure(fg='Green')
        self.BoardP.place(x=10, y=35, anchor=tk.W)

        if Mode == 1:
            self.ClassBoard = Borad()
            self.SaveDataBoard = False
            self.SaveDataBoard_IO = False
            self.Board_show()
            self.BoardLoop = InfiniteTimer(0.1, self.Board_show)
            self.BoardLoop.start()
        elif Mode == 2:
            self.CallKeyBorad()


        self.btn_cam = tk.Button(self, text="Choose", command=lambda :[self.callback_cam(),self.ViewImage()],bg='black')
        self.btn_cam.configure(font=("Arial", 18))
        self.btn_cam.configure(justify="center", foreground="green")
        self.btn_cam.place(x=1390, y=10)

        self.btn_add = tk.Button(self, text="Add Master", command=self.AddMaster,bg='black')
        self.btn_add.configure(font=("Arial", 18))
        self.btn_add.configure(justify="center", foreground="green")
        self.btn_add.place(x=1650, y=10)

        self.btn_reset = tk.Button(self, text="Initiated", command=self.ShowCount,bg='black')
        self.btn_reset.configure(font=("Arial", 18))
        self.btn_reset.configure(justify="center", foreground="green")
        self.btn_reset.place(x=700, y=10)

        #Logo = Image.open('Image/Logo_BKF.png')
        #Logo = ImageTk.PhotoImage(Logo)
        self.btn_Close = tk.Button(self, text="Exit", command=self.Destroy, bg='black')
        self.btn_Close.configure(font=("Arial", 18))
        self.btn_Close.configure(justify="center", foreground="red")
        self.btn_Close.place(x=1800, y=10, width=100)

        self.ShowCount()

        self.btn_repart = tk.Button(self, text="Re-order", command=self.CallPart,bg='black')
        self.btn_repart.configure(font=("Arial", 18))
        self.btn_repart.configure(justify="center", foreground="green")
        self.btn_repart.place(x=830, y=10)


        self.view = tk.Label(self,bg='black')
        self.view.place(x=950, y=180)

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
        if self.Sever_API == "Connected":
            self.Machine_Vision.configure(fg='Green')
            self.Machine_Version.configure(fg='Green')
        else:
            self.Machine_Vision.configure(fg='Red')
            self.Machine_Version.configure(fg='Red')
        if self.Batch_API_Get == self.Batch_API:
            pass
        elif self.Batch_API_Get != self.Batch_API:
            self.Batch_API_Get = self.Batch_API
            self.PARTP.configure(text=self.Part_API)
            self.PART_NAMEP.configure(text=self.part_name_API)
            self.CUSTOMER_NUMBERP.configure(text=self.Customer_API)
            self.BATCH_NUMBERP.configure(text=self.Batch_API)
            self.MOLD_NUMBERP.configure(text=self.Mode_API)
            self.Call_IMAGE()
            self.ShowCount()
            self.PrintText()

    def IMAGE(self):
        path = "IMAGE"
        try:
            os.mkdir(path)
        except OSError as error:
            print(error)

    def Printer(self):
        file_path = 'Counter_Printer.json'
        try:
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            data = {"Partnumber": self.Part_API, "Counter": 0, "Packing": self.Packing_API}
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=6)

    def PrintText(self):
        with open('Counter_Printer.json', 'r') as json_file:
            Data = json.loads(json_file.read())
        Packing_Couter = Data["Counter"]
        PackPart = Data["Partnumber"]
        self.PACKING_NUMBER = tk.LabelFrame(self, text="PACKING",bg='black')
        self.PACKING_NUMBER.configure(font=("Arial", 10))
        self.PACKING_NUMBER.configure(fg='Green')
        self.PACKING_NUMBER.place(x=720, y=220, height=60, width=225)
        self.PACKING_NUMBERP = tk.Label(self.PACKING_NUMBER, text=str(Packing_Couter) + "/" + str(self.Packing_API),bg='black')
        self.PACKING_NUMBERP.configure(font=("Arial", 22))
        self.PACKING_NUMBERP.configure(fg='Green')
        self.PACKING_NUMBERP.place(x=10, y=15, anchor=tk.W)

    def Couter_Printer(self):
        file_path = 'Counter_Printer.json'
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)

        packing_counter = data["Counter"] + 1
        pack_part = data["Partnumber"]
        if pack_part != self.Part_API:
            printer = {"Partnumber": self.Part_API, "Counter": 1, "Packing": self.Packing_API}
        else:
            printer = {"Partnumber": self.Part_API, "Counter": packing_counter, "Packing": self.Packing_API}

        if packing_counter >= self.Packing_API:
            printer = {"Partnumber": self.Part_API, "Counter": 0, "Packing": self.Packing_API}
            with open('Printer.txt', 'w') as f:
                f.write('Printer')

        with open(file_path, 'w') as json_file:
            json.dump(printer, json_file, indent=6)

    def AddMaster(self):
        self.Login = tk.Toplevel(self)
        self.Login.title("Login")
        self.Login.geometry('220x120')
        self.Login.configure(background='#D4D4D4')

        self.message = tk.StringVar()
        self.show_message = tk.Label(self.Login, text="", textvariable=self.message,bg='#D4D4D4')
        self.show_message.configure(font=("Arial", 13))
        self.show_message.place(x=10, y=90)

        self.Password = tk.StringVar()  # string variable
        self.BoxPassword = tk.Entry(self.Login, font="Arial", show='*', textvariable=self.Password,bg='#A1E9FF',fg='green')
        self.BoxPassword.configure(font=("Arial", 20))
        self.BoxPassword.place(x=20, y=10, width=180, height=35)

        def character_limit(Password):
            try:
                if len(Password.get()) > 0:
                    Password.set(Password.get()[6])
            except:
                pass

        self.Password.trace("w", lambda *args: character_limit(self.Password))
        self.chack_Value_Password = tk.IntVar(value=0)

        self.buttonLogin = tk.Button(self.Login, text="Login", command=self.Search,bg='black')
        self.buttonLogin.configure(font=("Arial", 13))
        self.buttonLogin.configure(justify="center", foreground="green")
        self.buttonLogin.place(x=80, y=50)

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
            self.Login.destroy()
            self.SaveMaster = tk.Toplevel(self)
            self.SaveMaster.title("Save Master")
            self.SaveMaster.geometry('280x350')
            self.SaveMaster.configure(background='#D4D4D4')

            Lable_Cam = tk.Label(self.SaveMaster, text="Cam :",bg='#D4D4D4')
            Lable_Cam.configure(font=("Arial", 20))
            Lable_Cam.configure(fg='Green')
            Lable_Cam.place(x=10, y=10)
            n = tk.StringVar()
            cam = ttk.Combobox(self.SaveMaster, width=8, height=80, textvariable=n)
            cam.configure(font=("Arial", 20))
            cam.configure(justify="center", foreground="green")
            if Quantity_Cam == 1:
                cam['values'] = ('Cam1')
            elif Quantity_Cam == 2:
                cam['values'] = ('Cam1', 'Cam2')
            elif Quantity_Cam == 3:
                cam['values'] = ('Cam1', 'Cam2', 'Cam3')
            elif Quantity_Cam == 4:
                cam['values'] = ('Cam1', 'Cam2', 'Cam3', 'Cam4')
            elif Quantity_Cam == 5:
                cam['values'] = ('Cam1', 'Cam2', 'Cam3', 'Cam4', 'Cam5')
            cam.current(0)
            cam.place(x=120, y=10)

            Lable_Point = tk.Label(self.SaveMaster, text="Point :",bg='#D4D4D4')
            Lable_Point.configure(font=("Arial", 20))
            Lable_Point.configure(fg='Green')
            Lable_Point.place(x=10, y=60)
            Point_Data = tk.StringVar()
            Chose_Point = ttk.Combobox(self.SaveMaster, width=8, height=80, textvariable=Point_Data)
            Chose_Point.configure(font=("Arial", 20))
            Chose_Point.configure(justify="center", foreground="green")
            Chose_Point['values'] = ('Point1', 'Point2', 'Point3', 'Point4', 'Point5', 'Point6', 'Point7', 'Point8', 'Point9', 'Point10')
            Chose_Point.current(0)
            Chose_Point.place(x=120, y=60)

            Score_Data_Outline = tk.StringVar()
            Lable_Score_Outline = tk.Label(self.SaveMaster, text="Outline :",bg='#D4D4D4')
            Lable_Score_Outline.configure(font=("Arial", 20))
            Lable_Score_Outline.configure(fg='Green')
            Lable_Score_Outline.place(x=10, y=110)
            Score_Show_Outline = tk.Entry(self.SaveMaster, font="Arial", textvariable=Score_Data_Outline,bg='#A1E9FF')
            Score_Show_Outline.configure(font=("Arial", 20))
            Score_Show_Outline.configure(fg='Green')
            Score_Show_Outline.place(x=120, y=110, width=150)

            Score_Data_Area = tk.StringVar()
            Lable_Score_Area = tk.Label(self.SaveMaster, text="Area :",bg='#D4D4D4')
            Lable_Score_Area.configure(font=("Arial", 20))
            Lable_Score_Area.configure(fg='Green')
            Lable_Score_Area.place(x=10, y=160)
            Score_Show_Area = tk.Entry(self.SaveMaster, font="Arial", textvariable=Score_Data_Area,bg='#A1E9FF')
            Score_Show_Area.configure(font=("Arial", 20))
            Score_Show_Area.configure(fg='Green')
            Score_Show_Area.place(x=120, y=160, width=150)

            def Save():
                Score_Outline = Score_Data_Outline.get()
                Score_Area = Score_Data_Area.get()
                Point = Point_Data.get()
                Cam = n.get()
                Emp_ID = self.Password.get()
                if Score_Outline != "" and Score_Area != "":
                    if int(Score_Outline) >= 500 and int(Score_Area) >= 550:
                        if Cam == "Cam1":
                            path = cv.cvtColor(frame0.read()[1], cv.COLOR_BGR2RGB)
                        elif Cam == "Cam2":
                            path = cv.cvtColor(frame1.read()[1], cv.COLOR_BGR2RGB)
                        elif Cam == "Cam3":
                            path = cv.cvtColor(frame2.read()[1], cv.COLOR_BGR2RGB)
                        PLTimg1 = Image.fromarray(path)
                        PLTimg1.save("Current.bmp")
                        Create = '' + self.Part_API + '/Master'
                        if not os.path.exists(Create):
                            os.makedirs(Create)
                        else:
                            pass
                        refPt = []
                        cropping = False

                        def click_and_crop(event, x, y, flags, param):
                            global refPt, cropping
                            image = clone.copy()

                            if event == cv.EVENT_LBUTTONDOWN:
                                refPt = [(x, y)]
                                cropping = True
                            elif event == cv.EVENT_LBUTTONUP:
                                refPt.append((x, y))
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
                                        Save_Data.Master(Left, Top, Right, Bottom, Score_Outline, Score_Area, Cam, Point, Emp_ID, self.Part_API)

                        path = r'Current.bmp'
                        image = cv.imread(path)
                        clone = image.copy()
                        cv.namedWindow(Point)
                        cv.setMouseCallback(Point, click_and_crop)
                        cv.imshow(Point, image)

            buttonSave = tk.Button(self.SaveMaster, text="Save", command=Save,bg='black')
            buttonSave.configure(font=("Arial", 30, "bold"))
            buttonSave.configure(justify="center", foreground="green")
            buttonSave.place(x=120, y=220, width=150, height=80)

            def score_limit(*args):
                s = Score_Data_Outline.get()
                if str.isdigit(s):
                    if len(s) > 3:
                        Score_Data_Outline.set(s[:3])
                else:
                    Score_Data_Outline.set(s[:0])

                x = Score_Data_Area.get()
                if str.isdigit(x):
                    if len(x) > 3:
                        Score_Data_Area.set(x[:3])
                else:
                    Score_Data_Area.set(x[:0])

            Score_Data_Area.trace("w", score_limit)
            Score_Data_Outline.trace("w", score_limit)
            self.SaveMaster.mainloop()

        else:
            self.message.set("Password not match")
            self.show_message.configure(fg="Red")

    def Call_IMAGE(self):
        try:
            image1 = Image.open(r"IMAGE" + "\\" + "" + self.Part_API + "" + ".png")
            resize_img = image1.resize((545, 340))
            self.test = ImageTk.PhotoImage(resize_img)
            self.image_show = tk.Label(image=self.test,bg="black")
            self.image_show.image = self.test
            self.image_show.place(x=395, y=305)
        except:
            pass

    def combobox_cam(self):
        self.n = tk.StringVar()
        self.cam = ttk.Combobox(self, width=8, height=80, textvariable=self.n)
        self.cam['state'] = 'readonly'
        self.cam.configure(font=("Arial", 20))
        #self.cam.configure(background= "white")
        self.cam.configure(justify="center", foreground="green",background="black")
        if Quantity_Cam == 1:
            self.cam['values'] = ('Cam1')
        elif Quantity_Cam == 2:
            self.cam['values'] = ('Cam1', 'Cam2')
        elif Quantity_Cam == 3:
            self.cam['values'] = ('Cam1', 'Cam2', 'Cam3')
        elif Quantity_Cam == 4:
            self.cam['values'] = ('Cam1', 'Cam2', 'Cam3', 'Cam4')
        elif Quantity_Cam == 5:
            self.cam['values'] = ('Cam1', 'Cam2', 'Cam3', 'Cam4', 'Cam5')
        self.cam.current(0)
        self.cam.place(x=1500, y=10,height=47)

    def callback_cam(self):
        self.Label_cam.configure(text=self.cam.get())

    def ShowCount(self):
        self.Close_Camera = False
        self.OK_Data = 0
        self.NG_Data = 0
        self.Result_Ok.configure(text="OK : "+str(self.OK_Data))
        self.Result_NG.configure(text="NG : "+str(self.NG_Data))

        #Save_Result(1)
        self.btn_reset.focus_set()
        self.Point_ = tk.LabelFrame(self, text="Point", borderwidth=3, relief="ridge", padx=5, pady=10,bg='black')
        self.Point_.configure(font=("Arial", 13))
        self.Point_.configure(fg='Green')
        self.Point_.place(x=5, y=300, height=700, width=60)

        self.Result_ = tk.LabelFrame(self, text="Result", borderwidth=3, relief="ridge", padx=5, pady=10,bg='black')
        self.Result_.configure(font=("Arial", 13))
        self.Result_.configure(fg='Green')
        self.Result_.place(x=70, y=300, height=700, width=80)

        self.Score_Outline = tk.LabelFrame(self, text="Outline", borderwidth=3, relief="ridge", padx=5, pady=10,bg='black')
        self.Score_Outline.configure(font=("Arial", 13))
        self.Score_Outline.configure(fg='Green')
        self.Score_Outline.place(x=155, y=300, height=700, width=110)

        self.Score_Area = tk.LabelFrame(self, text="Area", borderwidth=3, relief="ridge", padx=5, pady=10,bg='black')
        self.Score_Area.configure(font=("Arial", 13))
        self.Score_Area.configure(fg='Green')
        self.Score_Area.place(x=270, y=300, height=700, width=110)
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
            with open(self.Part_API + '/' + self.Part_API + '.json', 'r') as json_file:
                self.Master = json.loads(json_file.read())
            if self.count == len(self.Master):
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
                        tk.Label(self.Point_, text=(k + 1), borderwidth=1, relief="groove", padx=5, pady=8, font=("Arial", 18),bg='black',fg='Green').place(x=5, y=70 * k)
                        # tk.Label(self.Result_, text="N/A", borderwidth=3, relief="groove", padx=5, pady=10,font=("Arial", 18),fg='#A3A6AB').place(x=35, y=70*k)
                        # tk.Label(self.Score_Outline, text="", borderwidth=3, relief="groove", padx=55, pady=10,font=("Arial", 18)).place(x=2, y=70*k)
                        # tk.Label(self.Score_Area, text="", borderwidth=3, relief="groove", padx=55, pady=10,font=("Arial", 18)).place(x=2, y=70*k)
            else:
                messagebox.showwarning("Warning", "MasterImage & MasterData Dont's Match")
        except:
            pass

    def Camera(self):
        try:
                if Quantity_Cam == 1:
                    self.Run_Camera_1 = cv.cvtColor(frame0.read()[1], cv.COLOR_BGR2RGB)
                    img = Image.fromarray(self.Run_Camera_1)
                    resize_img = img.resize((540, 340))
                    imgtk = ImageTk.PhotoImage(image=resize_img)
                elif Quantity_Cam == 2:
                    self.Run_Camera_1 = cv.cvtColor(frame0.read()[1], cv.COLOR_BGR2RGB)
                    self.Run_Camera_2 = cv.cvtColor(frame1.read()[1], cv.COLOR_BGR2RGB)
                    if self.Label_cam['text'] == "Cam1":
                        img = Image.fromarray(self.Run_Camera_1)
                        resize_img = img.resize((540, 340))
                    elif self.Label_cam['text'] == "Cam2":
                        img = Image.fromarray(self.Run_Camera_2)
                        resize_img = img.resize((540, 340))
                    imgtk = ImageTk.PhotoImage(image=resize_img)
                elif Quantity_Cam == 3:
                    self.Run_Camera_1 = cv.cvtColor(frame0.read()[1], cv.COLOR_BGR2RGB)
                    self.Run_Camera_2 = cv.cvtColor(frame1.read()[1], cv.COLOR_BGR2RGB)
                    self.Run_Camera_3 = cv.cvtColor(frame2.read()[1], cv.COLOR_BGR2RGB)
                    if self.Label_cam['text'] == "Cam1":
                        img = Image.fromarray(self.Run_Camera_1)
                        resize_img = img.resize((540, 340))
                    elif self.Label_cam['text'] == "Cam2":
                        img = Image.fromarray(self.Run_Camera_2)
                        resize_img = img.resize((540, 340))
                    elif self.Label_cam['text'] == "Cam3":
                        img = Image.fromarray(self.Run_Camera_3)
                        resize_img = img.resize((540, 340))
                    imgtk = ImageTk.PhotoImage(image=resize_img)
                if self.Close_Camera == False:
                    self.frame.imgtk = imgtk
                    self.frame.configure(image=imgtk)
                self.after(60, self.Camera)
        except:
            messagebox.showerror('Python Error', 'Check Cameras')


    def Destroy(self):
        response = messagebox.askquestion("Close Programe", "Are you sure?", icon='warning')
        if response == "yes":
            if Quantity_Cam == 1:
                frame0.release()
            elif Quantity_Cam == 2:
                frame0.release()
                frame1.release()
            elif Quantity_Cam == 3:
                frame0.release()
                frame1.release()
                frame2.release()
            cv.destroyAllWindows()
            app.destroy()
            subprocess.call([r'TerminatedProcess.bat'])

    if Mode == 1:
        def Board_show(self):
                Login = False
                SaveMaster = False
                try:
                    self.Login.winfo_geometry()
                except:
                    Login = True
                try:
                    self.SaveMaster.winfo_geometry()
                except:
                    SaveMaster = True
                if Login == True and SaveMaster == True:
                    Hex = self.ClassBoard.ReadBorad()[0]
                    Bin = self.ClassBoard.ReadBorad()[2]
                    self.BoardP.configure(text=Hex)
                    if Bin == "110000001100000000110100001010":
                        self.SaveDataBoard = True
                    elif Bin == "110000001100010000110100001010" and self.SaveDataBoard == True:  # 01
                        try:
                            self.Close_Camera = True
                            self.ProcessP.configure(text="Process")
                            self.ProcessP.configure(fg='yellow')
                            Save_Data.Save_Imaga_Run(self.Run_Camera_1,self.Run_Camera_2,self.Run_Camera_3)
                            self.Main()
                            self.ShowScore()
                            self.ShowResult()
                            Save_Data.Save_Image(self.Part_API, self.count, self.ImageSave, self.Point_Left, self.Point_Top, self.Point_Right, self.Point_Bottom, self.Left_Find, self.Top_Find, self.Right_Find, self.Bottom_Find, self.Color,
                                                 self.Score_Outline_Data, self.Point_Score_Outline, self.Score_Area_Data, self.Point_Score_Area, self.Result, 30)
                            self.ViewImage()
                            self.ProcessP.configure(text="Ready")
                            self.ProcessP.configure(fg="green")
                            self.SaveDataBoard = False
                        except:
                            messagebox.showerror('Program Error', 'Process')
                    #self.after(100,self.Board_show)

    elif Mode == 2:
        def CallKeyBorad(self):
            self.LabelKeyBorad = tk.Label(self)
            self.LabelKeyBorad.bind_all('<KeyRelease>', self.Processing)
        def Processing(self, event):
            Login = False
            SaveMaster = False
            try:
                self.Login.winfo_geometry()
            except:
                Login = True
            try:
                self.SaveMaster.winfo_geometry()
            except:
                SaveMaster = True
            if self.count != 0 and Login == True and SaveMaster == True:
                    if event.char == '5':
                        self.Close_Camera = True
                        self.ProcessP.configure(text="Process")
                        self.ProcessP.configure(fg='yellow')
                        Save_Data.Save_Imaga_Run(self.Run_Camera_1,self.Run_Camera_2,self.Run_Camera_3)
                        self.Main()
                        self.ShowScore()
                        self.ShowResult()
                        Save_Data.Save_Image(self.Part_API, self.count, self.ImageSave, self.Point_Left, self.Point_Top, self.Point_Right, self.Point_Bottom, self.Left_Find, self.Top_Find, self.Right_Find, self.Bottom_Find, self.Color,
                                             self.Score_Outline_Data, self.Point_Score_Outline, self.Score_Area_Data, self.Point_Score_Area, self.Result,30)
                        self.ViewImage()
                        self.ProcessP.configure(text="Ready")
                        self.ProcessP.configure(fg="green")

    def Strat(self):
        self.Close_Camera = True
        self.ProcessP.configure(text="Process")
        self.ProcessP.configure(fg='yellow')
        Save_Data.Save_Imaga_Run(self.Run_Camera_1,self.Run_Camera_2,self.Run_Camera_3)
        self.Main()
        self.ShowScore()
        self.ShowResult()
        Save_Data.Save_Image(self.Part_API, self.count, self.ImageSave, self.Point_Left, self.Point_Top, self.Point_Right, self.Point_Bottom, self.Left_Find, self.Top_Find, self.Right_Find, self.Bottom_Find, self.Color,
                             self.Score_Outline_Data, self.Point_Score_Outline, self.Score_Area_Data, self.Point_Score_Area, self.Result, 30)
        self.ViewImage()
        self.ProcessP.configure(text="Ready")
        self.ProcessP.configure(fg="green")

    def Process_Outline(self, image, Template, Left, Top, Right, Bottom):
        image = cv.imread(image, 0)
        Template = cv.imread(Template, 0)
        w, h = Template.shape[::-1]
        c = 0
        TemplateThreshold = 0.7
        curMaxVal = 0
        curMaxTemplate = -1
        curMaxLoc = (0, 0)
        for meth in ['cv.TM_CCOEFF_NORMED']:
            method = eval(meth)
            try:
                image = image[(Top - 30):(Bottom + 30), (Left - 30):(Right + 30)]
                res = cv.matchTemplate(image, Template, method)
            except:
                image = image[Top:Bottom, Left:Right]
                res = cv.matchTemplate(image, Template, method)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
            if max_val > TemplateThreshold and max_val > curMaxVal:
                if method in [cv.TM_SQDIFF]:
                    top_left = min_loc
                else:
                    top_left = max_loc
                curMaxVal = max_val
                curMaxTemplate = c
                curMaxLoc = max_loc
            c = c + 1
            try:
                if curMaxTemplate == -1:
                    return (0, (0, 0), 0, 0, (0, 0))
                else:
                    bottom_right = (top_left[0] + w, top_left[1] + h)
                    return (curMaxTemplate % 3, curMaxLoc, 1 - int(curMaxTemplate / 3) * 0.2, curMaxVal, bottom_right)
            except:
                return (0, (0, 0), 0, 0, (0, 0))

    def Crop_image_Area(self, imgframe, Left, Top, Right, Bottom):
        img = cv.imread(imgframe, 0)
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

    def Process_Area(self,Master, Template):
        Score_Ture = []
        Result_Score = 0
        swapped = False
        Couter = len(Master)
        for i in range(Couter):
            if Master[i] < Template[i]:
                Score_Ture.append((Master[i] / Template[i]) * 1000)
            else:
                Score_Ture.append((Template[i] / Master[i]) * 1000)
        for n in range(len(Score_Ture) - 1, 0, -1):
            for i in range(n):
                if Score_Ture[i] > Score_Ture[i + 1]:
                    swapped = True
                    Score_Ture[i], Score_Ture[i + 1] = Score_Ture[i + 1], Score_Ture[i]
        for i in range(len(Score_Ture)):
            if i < 5:
                Result_Score += Score_Ture[i]
        Result_Score = int(Result_Score / 5)
        return Result_Score

    def Crop_find(self,image,Left,Top, Right,Bottom,top_left,bottom_right,scale):
        image = cv.imread(image, 0)
        if scale == 1:
            image = image[(Top - 30):(Bottom + 30), (Left - 30):(Right + 30)]
            Left = top_left[0]
            Top = top_left[1]
            Right = bottom_right[0]
            Bottom = bottom_right[1]
            image = image[Top:Bottom,Left:Right]
        else:
            image = image[Top:Bottom, Left:Right]
        return image

    def Main(self):
        if self.count != 0:
            self.sts = []
            self.Color = []
            self.ColorView = []
            self.Color_Show = []
            self.ImageSave = []
            self.Result = []
            self.Score_Outline_Data = []
            self.Score_Area_Data = []
            self.padx_outline = []
            self.padx_area = []
            self.place = []
            self.Left_Find = []
            self.Top_Find = []
            self.Right_Find = []
            self.Bottom_Find = []
            for x in range(self.count):
                if self.Point_Camera[x] == "Cam1":
                    image = r'Snap1.bmp'
                elif self.Point_Camera[x] == "Cam2":
                    image = r'Snap2.bmp'
                elif self.Point_Camera[x] == "Cam3":
                    image = r'Snap3.bmp'
                self.ImageSave.append(cv.imread(image))
                Template = r"" + self.Part_API + "\Master""\\""Point" + str(x + 1) + "_Template.bmp"
                (template, top_left, scale, val,bottom_right) = self.Process_Outline(image, Template, self.Point_Left[x], self.Point_Top[x], self.Point_Right[x], self.Point_Bottom[x])
                self.Left_Find.append(self.Point_Left[x]+top_left[0]-30)
                self.Top_Find.append(self.Point_Top[x]+top_left[1]-30)
                self.Right_Find.append(self.Point_Right[x]+top_left[0]-30)
                self.Bottom_Find.append(self.Point_Bottom[x]+top_left[1]-30)
                Template = cv.imread(Template, 0)
                Master = self.Crop_find(image,self.Point_Left[x], self.Point_Top[x], self.Point_Right[x], self.Point_Bottom[x],top_left,bottom_right,scale)
                Score_Area_Data = self.Process_Area(self.Rule_Of_Thirds(Master), self.Rule_Of_Thirds(Template))
                self.Score_Outline_Data.append(int(round(val * 1000, 0)))
                self.Score_Area_Data.append(Score_Area_Data)
                if ((val * 1000 )>= self.Point_Score_Outline[x]) and (Score_Area_Data >= self.Point_Score_Area[x]):
                    self.Result.append(1)
                    self.Color.append((0, 255, 0))
                    self.ColorView.append((0, 255, 0))
                    self.Color_Show.append("Green")
                    self.padx_outline.append(20)
                    self.padx_area.append(20)
                else:
                    self.Result.append(0)
                    self.Color.append((0, 0, 255))
                    self.ColorView.append((255, 0, 0))
                    self.Color_Show.append("Red")
                    if val * 1000 == 0:
                        self.padx_outline.append(32)
                    else:
                        self.padx_outline.append(20)
                    if  Score_Area_Data == 0:
                        self.padx_area.append(32)
                    else:
                        self.padx_area.append(20)
                self.place.append(x * 70)

    def ResultComfrim(self):
        if self.Comfrim_Data >= 4:
            self.NG_Data = self.NG_Data + 1
            Save_Data.Save_Score(self.Part_API, self.Batch_API, self.Machine_API, self.count, self.Score_Area_Data, self.Result)
            self.Result_NG.configure(text="NG : " + str(self.NG_Data))

    def ShowResult(self):
        if self.count != 0:
            for i in range(len(self.Result)):
                if self.Result[i] == 1:
                    if i == len(self.Result) - 1:
                        self.Couter_Printer()
                        self.PrintText()
                        self.OK_Data = self.OK_Data + 1
                        self.Comfrim_Data = 0
                        Save_Data.Save_Score(self.Part_API, self.Batch_API, self.Machine_API, self.count, self.Score_Area_Data, self.Result)
                        self.Result_Ok.configure(text="OK : " + str(self.OK_Data))
                        if Mode == 1 and self.SaveDataBoard_IO == False:
                            self.ClassBoard.inst.write("@1 R00")
                            self.SaveDataBoard_IO = True
                            self.ClassBoard.inst.clear()
                else:
                    self.Comfrim_Data = self.Comfrim_Data + 1
                    self.ResultComfrim()
                    if Mode == 1 and self.SaveDataBoard_IO == True:
                        self.ClassBoard.inst.write("@1 R40")
                        self.SaveDataBoard_IO = False
                        self.ClassBoard.inst.clear()
                    break

    def ShowScore(self):
        if self.count != 0:
            for i in range(self.count):
                if self.Result[i] == 1:
                    tk.Label(self.Result_, text="OK", borderwidth=3, relief="groove", bg=self.Color_Show[i], font=("Arial", 18), padx=10, pady=8).place(x=2, y=self.place[i])
                else:
                    tk.Label(self.Result_, text="NG", borderwidth=3, relief="groove", bg=self.Color_Show[i], font=("Arial", 18), padx=10, pady=8).place(x=2, y=self.place[i])
                tk.Label(self.Score_Outline, text=str(self.Score_Outline_Data[i]), borderwidth=3, relief="groove", font=("Arial", 18), padx=self.padx_outline[i], pady=8).place(x=2, y=self.place[i])
                tk.Label(self.Score_Area, text=str(self.Score_Area_Data[i]), borderwidth=3, relief="groove", font=("Arial", 18), padx=self.padx_area[i], pady=8).place(x=2, y=self.place[i])

    def ViewImage(self):
        if self.count != 0:
            try:
                if Quantity_Cam == 1:
                    image = cv.imread("Snap1.bmp")
                    image = cv.cvtColor(image ,cv.COLOR_BGR2RGB)
                    for s in range(self.count):
                        if self.cam.get() == "Cam1" and self.Point_Camera[s] == "Cam1":
                            cv.rectangle(image, (self.Left_Find[s], self.Top_Find[s]), (self.Right_Find[s], self.Bottom_Find[s]), self.ColorView[s], 2)
                            cv.rectangle(image, (self.Point_Left[s]-30, self.Point_Top[s]-30), (self.Point_Right[s]+30, self.Point_Bottom[s]+30), self.ColorView[s], 2)
                            cv.putText(image, "Point"+str(s+1), (self.Point_Left[s]-30, self.Point_Top[s]-30), cv.FONT_HERSHEY_SIMPLEX, 0.7, self.ColorView[s], 2)
                    im = Image.fromarray(image)
                    im = im.resize((960, 720))
                    image = ImageTk.PhotoImage(image=im)
                    self.view.image = image
                    self.view.configure(image=image)
                elif Quantity_Cam == 2:
                    image1 = cv.imread("Snap1.bmp")
                    image1 = cv.cvtColor(image1, cv.COLOR_BGR2RGB)
                    image2 = cv.imread("Snap2.bmp")
                    image2 = cv.cvtColor(image2, cv.COLOR_BGR2RGB)
                    for s in range(self.count):
                        if self.cam.get() == "Cam1" and self.Point_Camera[s] == "Cam1":
                            cv.rectangle(image1, (self.Left_Find[s], self.Top_Find[s]), (self.Right_Find[s], self.Bottom_Find[s]), self.ColorView[s], 2)
                            cv.rectangle(image1, (self.Point_Left[s]-30, self.Point_Top[s]-30), (self.Point_Right[s]+30, self.Point_Bottom[s]+30), self.ColorView[s], 2)
                            cv.putText(image1, "Point" + str(s + 1), (self.Point_Left[s]-30, self.Point_Top[s]-30), cv.FONT_HERSHEY_SIMPLEX, 0.7, self.ColorView[s], 2)
                            im = Image.fromarray(image1)
                        elif self.cam.get() == "Cam2" and self.Point_Camera[s] == "Cam2":
                            cv.rectangle(image2, (self.Left_Find[s], self.Top_Find[s]), (self.Right_Find[s], self.Bottom_Find[s]), self.ColorView[s], 2)
                            cv.rectangle(image2, (self.Point_Left[s]-30, self.Point_Top[s]-30), (self.Point_Right[s]+30, self.Point_Bottom[s]+30), self.ColorView[s], 2)
                            cv.putText(image2, "Point" + str(s + 1), (self.Point_Left[s]-30, self.Point_Top[s]-30), cv.FONT_HERSHEY_SIMPLEX, 0.7, self.ColorView[s], 2)
                            im = Image.fromarray(image2)
                    im = im.resize((960, 720))
                    image = ImageTk.PhotoImage(image=im)
                    self.view.image = image
                    self.view.configure(image=image)
                elif Quantity_Cam == 3:
                    image1 = cv.imread("Snap1.bmp")
                    image1 = cv.cvtColor(image1, cv.COLOR_BGR2RGB)
                    image2 = cv.imread("Snap2.bmp")
                    image2 = cv.cvtColor(image2, cv.COLOR_BGR2RGB)
                    image3 = cv.imread("Snap3.bmp")
                    image3 = cv.cvtColor(image3, cv.COLOR_BGR2RGB)
                    for s in range(self.count):
                        if self.cam.get() == "Cam1" and self.Point_Camera[s] == "Cam1":
                            cv.rectangle(image1, (self.Left_Find[s], self.Top_Find[s]), (self.Right_Find[s], self.Bottom_Find[s]), self.ColorView[s], 2)
                            cv.rectangle(image1, (self.Point_Left[s]-30, self.Point_Top[s]-30), (self.Point_Right[s]+30, self.Point_Bottom[s]+30), self.ColorView[s], 2)
                            cv.putText(image1, "Point" + str(s + 1), (self.Point_Left[s]-30, self.Point_Top[s]-30), cv.FONT_HERSHEY_SIMPLEX, 0.7, self.ColorView[s], 2)
                            im = Image.fromarray(image1)
                        elif self.cam.get() == "Cam2" and self.Point_Camera[s] == "Cam2":
                            cv.rectangle(image2, (self.Left_Find[s], self.Top_Find[s]), (self.Right_Find[s], self.Bottom_Find[s]), self.ColorView[s], 2)
                            cv.rectangle(image2, (self.Point_Left[s]-30, self.Point_Top[s]-30), (self.Point_Right[s]+30, self.Point_Bottom[s]+30), self.ColorView[s], 2)
                            cv.putText(image2, "Point" + str(s + 1), (self.Point_Left[s]-30, self.Point_Top[s]-30), cv.FONT_HERSHEY_SIMPLEX, 0.7, self.ColorView[s], 2)
                            im = Image.fromarray(image2)
                        elif self.cam.get() == "Cam3" and self.Point_Camera[s] == "Cam3":
                            cv.rectangle(image3, (self.Left_Find[s], self.Top_Find[s]), (self.Right_Find[s], self.Bottom_Find[s]), self.ColorView[s], 2)
                            cv.rectangle(image3, (self.Point_Left[s]-30, self.Point_Top[s]-30), (self.Point_Right[s]+30, self.Point_Bottom[s]+30), self.ColorView[s], 2)
                            cv.putText(image3, "Point" + str(s + 1), (self.Point_Left[s]-30, self.Point_Top[s]-30), cv.FONT_HERSHEY_SIMPLEX, 0.7, self.ColorView[s], 2)
                            im = Image.fromarray(image3)
                    im = im.resize((960, 720))
                    image = ImageTk.PhotoImage(image=im)
                    self.view.image = image
                    self.view.configure(image=image)
            except:
                pass

if __name__ == "__main__":
    app = App()
    app.mainloop()