import requests
import sys
import os


def sendmsg(msg,token,chat_id):
    #send message from token bot to user under chat_id
    print(msg)
    para= {"chat_id":chat_id,"text":msg}
    resp = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?"
    ,params=para)

def getfilecontent(filename):
    #if filename exists, return its content as string.
    if filename in os.listdir():
        with open(filename,mode = "r") as file:
            return file.read()
    else:
        return "no such file found"

def read_bot_data(filename):
    #read bot data from file and return as [token,chat_id]
    try:
        with open(filename,mode="r") as file:
            data = file.read().splitlines()
            data[0] = data[0].replace('token=','')
            data[1] = data[1].replace('chat_id=','')
            return data
    except:
        print("Unable to read Bot_data, check format again.")
        sys.exit()

#main
if len(sys.argv) != 3:
    print("need exactly 2 arguments. 1: bot_data  2:file_to_send")
else:
    data = read_bot_data(sys.argv[1])
    print(f"send message to: {data[1]}\n")
    try:
        sendmsg(getfilecontent(sys.argv[2]),data[0],data[1])
    except:
        print("unable to send message!")
