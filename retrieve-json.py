import pycurl
import json
from io import BytesIO
import numpy
import PySimpleGUI as sg
import time

#Variables#

host="localhost"
port="9090"

#Functions#

def get_miners():
    minerlist=numpy.empty((0,3),str)
    config=open("minerconfig.cfg","r")
    next(config)
    for miner in config:
        miner=miner.rstrip()
        temparr=numpy.array(miner.split(","))
        minername=temparr[0]
        mineripaddr=temparr[1]
        minerport=temparr[2]
        minerlist=numpy.append(minerlist,numpy.array([[minername,mineripaddr,minerport]]),axis=0)
    return minerlist

def get_data(host,port):
    buffer = BytesIO()
    urlstr="http://{}:{}/stats".format(host,port)
    query=pycurl.Curl()
    query.setopt(pycurl.URL,urlstr)
    query.setopt(pycurl.WRITEFUNCTION, buffer.write)
    query.perform()
    query.close()
    querydata=json.loads(buffer.getvalue())
    return querydata

###MAIN###
minerdata=[]
miners=get_miners()
size=miners.shape
layout = [[sg.Text("Refreshing",size=(80,(size[0]*8)),key='-DATA-')],[sg.Text("Timestamp",size=(40,5),key='-TIME-')], [sg.Button("Refresh")],[sg.Button("Close")]]
window = sg.Window("Miner Watch", layout)
window.read()
n=0
while True:
    # End program if user closes window or
    # presses the OK button
    event, values = window.read(timeout=1)
    if event == sg.WIN_CLOSED or event == "Close":
        break
    miners=get_miners()
    minerdata=[]
    for miner in miners:
        minerdata.append("Name: "+get_data(miner[1],miner[2])["Devices"][0]["GPU 0"]["Name"])
        minerdata.append("Temperature(C): "+str(get_data(miner[1],miner[2])["Devices"][0]["GPU 0"]["Temperature"]))
        for entries in get_data(miner[1],miner[2])["Devices"][0]["GPU 0"]:
            try:
                if "Power" in entries:
                    minerdata.append("Watts: "+str(get_data(miner[1],miner[2])["Devices"][0]["GPU 0"]["Power"]))
            except KeyError:
                    minerdata.append("Watts: Cannot Retrieve")
        minerdata.append("Accepted Shares: "+str(get_data(miner[1],miner[2])["Algorithms"][0]["Kawpow"]["Total"]["Accepted"]))
        minerdata.append("Hashrate: "+str(get_data(miner[1],miner[2])["Algorithms"][0]["Kawpow"]["Total"]["Hashrate"]))
        minerdata.append("-----------------------------------------")
    text='\n'.join([str(i) for i in minerdata])
    window['-DATA-'].update(text)
    window['-TIME-'].update("Uptime: "+str(n)+" seconds")
    window.Refresh()
    n=n+1
    time.sleep(1)

