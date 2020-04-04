from bs4 import BeautifulSoup
from time import time
import mechanicalsoup
import os
import shutil



def logwrite(text,reset = False):
    #write text to logfile. set reset to True, to reset the logfile
    if reset:
        try:
            with open("isislog.txt",mode = 'w') as f:
                pass
        except:
            print("unable to reset to logfile")
    else:
        print(str(text))
        try:
            with open("isislog.txt",mode = 'a') as logfile:
                logfile.write(str(text)+"\n")
        except:
            print("unable to write to logfile")

def namify(name):
    #turn string into viable filename
    valid='-_.() abcdefghijklmnopqrstuvwxyzöäüABCDEFGHIJKLMNOPQRSTUVWXYZÖÄÜ0123456789'
    filename = ''.join(c for c in name if c in valid)
    return filename


def get_name_from_tag(tag):
    #take html tag, if isis displays it as a name, return that name
    downloadname = None
    for child in tag.findChildren('span'):
       child = str(child)
       if'"instancename">' in child and '<span class=' in child:
           downloadname = namify(child.split('"instancename">')[1].split('<span class=')[0])
    if downloadname == None: #Special rule for FOSA
        tag = str(tag)
        if '>' in tag and '</a>' in tag and len(tag.split('>'))==3:
            downloadname = namify(tag.split('>')[1].split('</a')[0])
    return downloadname


def movefiles(src,dst,list):
    #moves all files from src to dst, whose names contain at least one of the
    #terms given in list
    count = 0
    if os.path.exists(src) and os.path.exists(dst):
        try:
            files = [f for f in os.listdir(src) if os.path.isfile(os.path.join(src,f))]
            for name in files:
                if any(s in name for s in list):
                    shutil.move(os.path.join(src,name),dst)
                    count += 1
            logwrite(str(count)+" files have been moved from " + str(scr) +" to " +
            str(dst))
        except:
            print("unable to move files")
    else:
        logwrite("path is not valid. src:" + str(scr) +" dst: " +str(dst))


def simpledownload(browser,folder,format=None,ignorefile='none'):
    #Download all pdf's on current page and save them in folder. Requires
    #Browser instance. 'format' allows filtering of availible links for a
    #given string. ignorefile takes filepath, where list of links not resulting
    #in a pdf are stored. On next call, these links won't be checked -> Speedup

    soup = browser.get_current_page()

    #Get all links on current site as (link,name) tuple. Use 'format' to filter.
    #To avoid problems, links are screened for keywords -> possible to miss some.
    #If 'format' is not used, links won't be screened
    linklist = []
    print("found links:")
    if format != None:
        for link in soup.find_all('a', href=True):
            if format in link['href']:
                    linklist.append((link['href'],get_name_from_tag(link)))
    else:#filter out links like logout
        filterout = ["login","logout","lang=","/quiz/","/forum/","/calendar/",
        "/admin/","/grade/","/local/","/etherpadlite/","/user/","/enrol/",
        "/message/","/course/view.php?id=","/assign/","/choicegroup/",
        "/recent.php?id"]
        for link in soup.find_all('a', href=True):
            linkname = str(link['href'])
            if "https://isis.tu-berlin.de/" in linkname:
                if not any(s in linkname for s in filterout):
                    linklist.append((str(link['href']),get_name_from_tag(link)))

    #Remove duplicates. If in doubt, keep those with specified Downloadname.
    removelist = []
    doublelist = []
    for entry1 in linklist:
        for entry2 in linklist:
            if entry1[0] == entry2[0]:
                if entry1 != entry2:
                    if entry1[1] == None:
                        removelist.append(entry1)
                    else:
                        removelist.append(entry2)
                else:
                    doublelist.append(entry1)
    for entry in doublelist:
        while linklist.count(entry)>1:
            linklist.remove(entry)
    linklist = [x for x in linklist if x not in removelist]
    #Turn links whose name is '' into None
    for entry in linklist:
        if entry[1] == '':
            linklist.append((entry[0],None))
            linklist.remove(entry)
    #Handle identically named,yet different links
    for entry1 in list(linklist):
        for entry2 in list(linklist):
            if entry1[1]==entry2[1]:
                if entry1[0] != entry2[0]:
                    if entry1[1] != None:
                        linklist.append((entry1[0],list(entry1)[1]+"_0"))
                        linklist.remove(entry1)
                        if linklist.count(entry1) <1:
                            break

    #Remove in ingorefile listed links:
    if ignorefile != 'none':
        try:
            file = open(ignorefile,mode="a+")
            file.seek(0)
            ignorelinks = file.read().splitlines()
            for entry in list(linklist):
                if entry[0] in ignorelinks:
                    linklist.remove(entry)
        except:
            print("unable to open ignorefile :"+str(ignorefile))
    #Display all found links
    for i in linklist:
        print(i)

    def download(browser,linktuple,folder):
        #Download link and save as name in folder. If name = None, get new name,
        link = str(linktuple[0])
        filename = linktuple[1]
        #Check already downloaded files
        if filename != None and (filename in os.listdir(folder) or
        filename+".pdf" in os.listdir(folder)):
            print("file already downloaded")
        else:
            timer = time()
            response = browser.open(link)
            if ".pdf" in browser.get_url():
                if filename == None or filename == '':
                    #Get new name
                    filename = "newfile"
                    try:
                        url = browser.get_url()
                        filename = url.split(".pdf")[0].split("/")[-1]
                        if len(url.split('/'))>4:
                            number = url.split('/')[4]
                        else:
                            number = "nope"
                            logwrite("link " + link + " does not contain file-id")
                        if number.isdigit():
                            filename += "_" + number
                    except:
                        logwrite("problem with "+ link)
                    #Handle duplicate names
                    if (filename in os.listdir(folder) or
                    (filename+".pdf" in os.listdir(folder))):
                        print("already downloaded")
                        return
                try:
                    #Download file
                    with open(folder+"/"+filename, 'wb') as f:
                        f.write(response.content)
                    logwrite("Downloaded file "+ filename + " in "
                    +str(round((time()-timer),6))+ " seconds")
                except:
                    logwrite("unable to download " + link + " " +filename)
            else:
                print("file is not pdf")
                if ignorefile != 'none':
                    file.write(link+"\n")

    print("\n")
    for link in linklist:
        download(browser,link,folder)
    if ignorefile != 'none':
        file.close()


def setup_browser(username,password):
    #Open browser,login and navigate to main ISIS screen. Return browser
    isisurl = "https://isis.tu-berlin.de/login/index.php"
    browser = mechanicalsoup.StatefulBrowser()
    browser.open(isisurl)
    browser.select_form('#shibboleth_login')
    response =browser.submit_selected()
    browser.select_form('form')
    response2 = browser.submit_selected()
    browser.select_form('form')
    browser["j_username"] = username
    browser["j_password"] = password
    browser.submit_selected()
    return browser


def get_courses(browser,ignore = []):
    #Find all availible courses and return them as list of (link,name) tuples.
    #'ignore' takes list of courses names, which will be excluded.
    soup = browser.get_current_page()
    #Find course names
    filter_tags = ["Meine Kurse","Alle Kurse","Kalender","Meine Startseite"]
    link_name_list = []
    for link in soup.find_all('span', class_= "media-body"):
        if not any(x in str(link) for x in filter_tags):
            if '</span>' in str(link) and '"media-body">' in str(link):
                link_name_list.append(str(link).split('"media-body">')[1].split("</span>")[0])
    #Find all links that lead to a course site. Order corrosponds to link names
    link_list = []
    for link in soup.find_all('a', href=True):
        if "https://isis.tu-berlin.de/course/view.php?id="in link['href']:
            if link['href'].split("view.php?id=")[1].isdigit():
                link_list.append(link['href'])
    #Remove courses to be ignored
    if isinstance(ignore,str):
        ignore.split(',')
    if ignore != [] and ignore != ["none"]:
        if len(link_list) == len(link_name_list):
            for course in list(link_name_list):
                if course in ignore:
                    del link_list[link_name_list.index(course)]
                    link_name_list.remove(course)
        else:
            print("Error: unable to find courses")
    print("Availible courses:")
    #Clean course names and return as list of (link,name) tuples
    link_name_list = [namify(i) for i in link_name_list]
    for course in link_name_list:
        print(course)
    print("")
    return list(zip(link_list,link_name_list))


def logout(browser):
    #End programm and logout
    logwrite("programm finished sucessfully")
    try:
        browser.open("https://isis.tu-berlin.de/login/logout.php")
        browser.select_form('form[action="https://isis.tu-berlin.de/login/logout.php"]')
        browser.submit_selected()
    except:
        pass


def get_data(datafile):
    #Read data from datafile. Lines in datafile corrospond to:
    #0=username
    #1=password
    #2=subjects to be ignored. use 'none' if all subjects are wanted
    #3=path where course folders will be created. Use "none" for current dir
    try:
        with open(datafile) as dfile:
            data = dfile.read().splitlines()
        if len(data) == 4:
            return data
        else:
            print("wrong dataformat. Line 1 = username, 2 = password, 3=subjects"
            +" to be ignored, use 'none' to get all. 4 = path to save files." +
            " Use 'none' for current dir")
            raise SystemExit
    except:
        print("unable to read datafile " + str(datafile))
        raise SystemExit

def standartrun(browser,course_list,savepath = os.getcwd(), ignore = "isisignorefile.txt"):
    #Take browser and download all files for all courses in course_list.
    #Folders for each course are created under savepath. To speedup
    #the process, links that didn't result in a pdf can be safed under "ignore"

    #Reset logfile
    logwrite("",reset=True)
    #Prevent ignorefile from becoming too big
    if ignore != "none":
        ig = open(ignore,'r')
        ig.seek(0)
        if len(ig.readlines())>80:
            ig.close()
            ig = open(ignore,'w')
            ig.close()
        else:
            ig.close()
    #Create course folders in savepath
    if savepath != "none":
        coursefolders = os.listdir(savepath)
        for course in course_list:
            if course[1] not in coursefolders:
                os.mkdir(os.path.join(savepath,course[1]))
    else:
        coursefolders = os.listdir(os.getcwd())
        for course in course_list:
            if course[1] not in coursefolders:
                os.mkdir(os.path.join(os.getcwd(),course[1]))
    #Download all courses
    for link in course_list:
        browser.open(link[0])
        print("Starting downloads for "+link[1]+":")
        simpledownload(browser,os.path.join(savepath,link[1]),
        ignorefile= ignore)
        print("\n")



################################################################################
data = get_data("data.txt")
browser = setup_browser(data[0],data[1])
course_list = get_courses(browser,ignore=data[2])
standartrun(browser,course_list,savepath = data[3])

###ADD YOUR CODE BELOW:###




###ADD YOUR CODE ABOVE###

logout(browser)
################################################################################
