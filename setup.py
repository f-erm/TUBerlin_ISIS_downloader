from isisdownloader import setup_browser,get_courses
from getpass import getpass
import os


def display_data(data):
    #Display all the data in data
    print("Username: "+data[0])
    pw = '*'*len(data[1])
    print("Password: "+pw)
    print("Courses to be downloaded: ",end='')
    for i in data[2]:
        print(i, end = '')
        if data[2].index(i) != len(data[2])-1:
            print(" , ",end='')
    print("\n",end='')
    if data[3]=="":
        print("Path to store your files: current dir")
    else:
        print("Path to store your files: "+data[3])
    print("Sites to also be downloaded: ")
    counter = 4
    while len(data)>counter:
        split = data[counter].split(";;")
        if not data[counter]=='':
            if len(split)==2:
                print(split[0]+" under "+split[1])
            else:
                raise Exception("Something wrong with your Datafile")
        counter += 1


def setup():
    print("Setting up your data:")
    data = []
    #Get username
    un = input("Enter your tuBIT username: ")
    data.append(un)
    #Get pw
    pw = getpass("Enter your password: ")
    data.append(pw)
    #Display availible courses
    print("Logging into ISIS, this might take a few seconds...")
    try:
        browser = setup_browser(un,pw)
    except:
        print("Unable to log into ISIS")
        os._exit(1)
    subjects = get_courses(browser,cleaned=False)
    print("Availible courses:")
    for c, course in enumerate(subjects,start=1):
        print(str(c)+": "+course[1])
    #Get Courses to be downloaded
    succes = False
    while not succes:
        inp= input("Enter courses you want to download, divided by ','. Press return to get all. Example: 1,3,6\n")
        if inp != "":
            inp = inp.split(',')
            for i in inp:
                if i.isdigit() and int(i)<=len(subjects):
                    succes = True
                else:
                    print("Input in wrong format. Example for right format: 1,5,8")
                    succes = False
                    break
        else:
            inp = list(range(len(subjects)))
            succes = True
    courselist = [subjects[int(i)-1][1] for i in inp]
    data.append(courselist)
    #Get Path
    path = '%'
    while not (os.path.exists(path) or path==""):
        path = input("Enter path in which course folders will be created, press return to select current folder:\n")
        if path != "" and not os.path.exists(path):
            print(path + " is not a valid path")
    data.append(path)
    #Get additional sites
    extra = ""
    while extra != "pass":
        extra = input("Do you want to add any other sites to download? By default the script will only check a courses mainpage. "+
         "Pages that contain files, but are not a courses mainpage, need to be added manualy.\n"+
         "Write them as '<url>;;<folderpath where you want store the files>' . If you do not want to add anything or are finished, write 'pass':\n")
        if extra != "pass":
            if ";;" in extra:
                split = extra.split(";;")
                if len(split)==2:
                    if os.path.exists(split[1]):
                        print("\nAdded url "+split[0]+ " under folderpath "+split[1]+" to also be downloaded")
                        data.append(extra)
                    else:
                        print("Folder "+split[1]+" does not exist.")
                else:
                    print("wrong format. Example: https://isis.tu-berlin.de/my/;;/home/user/projects/")

            else:
                print("wrong format. Example: https://isis.tu-berlin.de/my/;;/home/user/projects/")
    #Return data
    print("\nYour data:")
    display_data(data)
    return data


datafile_name = "data.txt"
#Open file and save lines in data list. data[2] is a list itself
print("Hello and welcome to the TU-Berlin Isis-Downloader setup")
try:
    if datafile_name in os.listdir():
        with open(datafile_name, "r") as datafile:
            datafile.seek(0)
            data=datafile.read().splitlines()
            if len(data)>2:
                data[2]=data[2].split(';;')
    else:
        data = []
except:
    print("unable to to read data.txt")
    os._exit(1)
#If file is empty, therefore new, set it up
if len(data)<2:
    data = setup()
#File is not new. Display content and ask if change is wanted
else:
    print("Current data:")
    display_data(data)
    answer = ''
    while answer != "n" and answer != "y":
        answer = input("\nDo you want to change something? y/n ")
    if answer == "n":
        print("No changes made")
    else:
        data = setup()
#Convert data[2] from list back to string
data[2] = "".join([c+";;" for c in data[2]])[:-2]
#Save data in file
datafile = open(datafile_name,mode='w')
datafile.seek(0)
for d in data:
    datafile.write(d+"\n")
datafile.close()
print("\nSetup finished, run main.py to continue")
