from isisdownloader import isisdownloader, get_data
from getpass import getpass
import os


def display_data(data):
    '''Display all the data in data'''
    print("Username: "+data[0])
    pw = '*'*len(data[1])
    print("Password: "+pw)
    print("Courses to be downloaded: ",end='')
    print(data[2])
    if data[3]=="none" or data[3]==None:
        print("Path to store your files: current dir")
    else:
        print("Path to store your files: " + data[3])
    if data[4]=="none" or data[4]==None:
        print("no ignorefile used")
    else:
        print("Ignorefile: " + data[4])
    print("Sites to also be downloaded: ")
    for c in data[5:]:
        split = c.split(";;")
        try:
            print(split[0]+" under "+split[1])
        except:
            raise Exception("Something wrong with your Datafile")


def setup():
    '''Gather the needed information from the user and return it as a list'''
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
        browser = isisdownloader(un,pw)
    except:
        print("Unable to log into ISIS")
        os._exit(1)
    subjects = browser.get_courses()
    print("Availible courses:")
    for c, course in enumerate(subjects,start=1):
        print(str(c)+": "+course[1])
    #Get Courses to be downloaded
    succes = True
    while succes:
        succes = False
        inp = input("\nEnter courses you want to download, divided by ','. Press return to get all. Example: 1,3,6\n")
        if inp == "":
            inp = list(range(len(subjects)))
            break
        else:
            inp =inp.split(',')
            for i in inp:
                if (not i.isdigit()) or int(i)>len(subjects):
                    print("Input in wrong format. Example for right format: 1,5,8")
                    succes = True
                    break
    courselist = [subjects[int(i)-1][1] for i in inp]
    data.append(courselist)
    #Get Path
    path = '%'
    while not os.path.exists(path):
        path = input("\nEnter path in which course folders will be created, press return to select current folder:\n")
        if path == "":
            path = "none"
            break
        if not os.path.exists(path):
            print(path + " is not a valid path")
    data.append(path)
    #get ignorefile
    ign = "%"
    while not os.path.isfile(ign):
        ign = input("\nEnter ignorefile to be used. Press return to continue without:\n")
        if ign == "":
            ign = "none"
            break
        if not os.path.isfile(ign):
            print(ign + " is not a valid file")
    data.append(ign)
    #Get additional sites
    extra = "%"
    while extra != "":
        extra = input("\nDo you want to add any other sites to download? By default the script will only check a courses mainpage. "+
         "Pages that contain files, but are not a courses mainpage, need to be added manualy.\n"+
         "Write them as '<url>;;<folderpath where you want store the files>' . If you do not want to add anything or are finished, press return:\n")
        if extra != "":
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
    return data


if __name__ == "__main__":
    datafile_name = "data.txt"
    #Open file and save lines in data list. data[2] is a list itself
    print("Hello and welcome to the TU-Berlin Isis-Downloader setup")
    try:
        data = get_data(datafile_name)
    except:
        if datafile_name in os.listdir():
            print("Unable to to read data.txt . Continue to overwrite it ")
        data = setup()
    #Display content and ask if change is wanted
    answer = ''
    while answer != "n" and answer != "y":
        print("Current data:")
        display_data(data)
        answer = input("\nDo you want to change something? y/n ")
        if answer == "y":
            data = setup()
            answer = ""
    #Convert data[2] from list back to string
    data[2] = "".join([c+";;" for c in data[2]])[:-2]
    #Save data in file
    with open(datafile_name,mode='w') as datafile:
        #datafile.seek(0)#############################################################################
        for d in data:
            datafile.write(d+"\n")
    print("\nSetup finished, run main.py to continue")
