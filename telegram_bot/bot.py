import requests
import sys
import os

#Silent-mode to be added later. For now, just mute the bot yourself
#Does not accept special characters like '#'.
#See "valid" in line 39 to see all valid characters


######################### YOUR DATA HERE #############################
token = ""
chat_id = 
######################### YOUR DATA HERE #############################


def sendmsg(msg,token,chat_id):
    #send message from token bot to user under chat_id
    msg = str(msg)
    print(msg)
    resp = requests.get("https://api.telegram.org/bot"+str(token)+
    "/sendMessage?chat_id="+str(chat_id)+"&text="+msg)

def getfilecontent(filename):
    #if filename exists, return its content as string.
    if filename in os.listdir():
        with open(filename,mode = "r") as file:
            return file.read()
    else:
        return "no such file found"

#main
if len(sys.argv) != 2:
    print("need exactly 1 argument")
else:
    if isinstance(sys.argv[1],str):
        print("send message to: "+str(chat_id))
        try:
            msg = getfilecontent(sys.argv[1])
            #clean message
            valid='?-_.() abcdefghijklmnopqrstuvwxyzöäüABCDEFGHIJKLMNOPQRSTUVWXYZÖÄÜ0123456789\n'
            msg = ''.join(c for c in msg if c in valid)
            sendmsg(msg,token,chat_id)
        except:
            print("unable to send message!")
    else:
        print("argument needs to be string")
