import json
with open('D:\labview vision\Python Build\Lib\TBA0A68RCO\TBA0A68RCO.json', 'r') as json_file:
    Setting_Paramiter = json.loads(json_file.read())
print(len(Setting_Paramiter))