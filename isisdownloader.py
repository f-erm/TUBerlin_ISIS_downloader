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
            print("unable to reset logfile")
    else:
        print(str(text))
        try:
            with open("isislog.txt",mode = 'a') as logfile:
                logfile.write(str(text)+"\n")
        except:
            print("unable to write to logfile")

def namify(name):
    #turn string into viable filename
    valid ="-_.() abcdefghijklmnopqrstuvwxyzöäü"\
    "ABCDEFGHIJKLMNOPQRSTUVWXYZÖÄÜ0123456789"
    filename = ''.join(c for c in name if c in valid)
    return filename


def get_name_from_tag(tag):
    #take html tag, if isis displays it as a name, return that name
    downloadname = None
    for child in tag.findChildren('span'):
       child = str(child)
       if'"instancename">' in child and '<span class=' in child:
           downloadname = namify(
           child.split('"instancename">')[1].split('<span class=')[0])
    #Special rules (i.e FOSA)
    if downloadname == None:
        tag = str(tag)
        if '>' in tag and '</a>' in tag and len(tag.split('>'))==3:
            downloadname = namify(tag.split('>')[1].split('</a')[0])
    #Turn '' into None
    if not downloadname:
        downloadname = None
    return downloadname


def movefiles(src,dst,list):
    #moves all files from src to dst, whose names contain >= 1 of terms in list
    count = 0
    if os.path.exists(src) and os.path.exists(dst):
        try:
            files = [f for f in os.listdir(src)
            if os.path.isfile(os.path.join(src,f))]
            for name in files:
                if any(s in name for s in list):
                    shutil.move(os.path.join(src,name),dst)
                    count += 1
            logwrite(f"{str(count)} files moved from {str(scr)} to {str(dst)}")
        except:
            print("unable to move files")
    else:
        logwrite(f"path is not valid. src:{str(scr)} dst: {str(dst)}")


def get_subfolders(folder):
    #return content of folder and and all its subfolders
    list = []
    list.extend([f for f in os.listdir(folder)
    if os.path.isfile(os.path.join(folder,f))])
    for sub in [d for d in os.listdir(folder)
    if os.path.isdir(os.path.join(folder, d))]:
        list.extend(get_subfolders(os.path.join(folder,sub)))
    return list


def download(linktuple,browser,folder):
    #Download link and save as name in folder. If name = None, get new name
    #If link is not pdf return it, else return None
    link = linktuple[0]
    filename = linktuple[1]
    timer = time()
    response = browser.open(link)
    if ".pdf" in browser.get_url():
        if filename == None:
        #get new name
            filename = "newfile"
            try:
                url = browser.get_url()
                filename = url.split(".pdf")[0].split("/")[-1]
                if len(url.split('/'))>4:
                    number = url.split('/')[4]
                else:
                    number = "no"
                    logwrite("link " + link + " does not contain file-id")
                if number.isdigit():
                    filename += "_" + number
            except:
                logwrite("problem with "+ link)
                return None
            #check if file already exists
            fcont = get_subfolders(folder)
            if filename in fcont or f"{filename}.pdf" in fcont:
                print("downloaded file already exists")
                return None
        try:
            #Download file
            with open(folder+"/"+filename+".pdf", 'wb') as f:
                f.write(response.content)
            logwrite("Downloaded file "+ filename + " in "
            +str(round((time()-timer),6))+ " seconds")
        except:
            logwrite("unable to download " + link + " " +filename)
        return None
    else:
        print("file is not pdf")
        return link


def simpledownload(browser,folder,ignorefile="isisignorefile.txt"):
    #Download all pdf's on current page and save them in folder. Ignorefile
    #can be uses to save links, not resulting in a pdf, for the next run.
    soup = browser.get_current_page()
    linklist = []
    print("found links:")
    #Get all links on current site as (link,name) and filter for keywords
    filterout = ["login","logout","lang=","/quiz/","/forum/","/calendar/",
    "/admin/","/grade/","/local/","/etherpadlite/","/user/","/enrol/",
    "/message/","/course/view.php?id=","/assign/","/choicegroup/",
    "/recent.php?id","/questionnaire/","/glossary/"]
    for link in soup.find_all('a', href=True):
        linkstr = str(link['href'])
        if "https://isis.tu-berlin.de/" in linkstr:
            if not any(s in linkstr for s in filterout):
                linkname = get_name_from_tag(link)
                #filter out duplicates and resolve naming issues
                if not any(linkstr== l[0] for l in linklist):
                    linklist.append((linkstr,linkname))
                count = "_0"
                for l in list(linklist):
                    if l[0]==linkstr:
                        if l[1]==None and linkname != None:
                            linklist.append((linkstr,linkname))
                            linklist.remove(l)
                        else:
                            linkname = None
                    if l[1]==linkname and l[1] != None:
                        linklist.append((l[0],l[1]+count))
                        linklist.remove(l)
                        count += "_0"
    #Remove in ingorefile listed links:
    if ignorefile != None:
        try:
            file = open(ignorefile,mode="a+")
            file.seek(0)
            ignorelinks = file.read().splitlines()
            for entry in list(linklist):
                if entry[0] in ignorelinks:
                    linklist.remove(entry)
        except:
            print("unable to open ignorefile :"+str(ignorefile))
            ignorefile = None
    #Display all found links
    for i in linklist:
        print(i)
    print("\n")
    #remove already downloaded links and sort by name/no name
    foldercontent=get_subfolders(folder)
    namelist = []
    nonelist = []
    ignorelist = []
    for f in linklist:
        if f[1] in foldercontent or f"{f[1]}.pdf" in foldercontent:
            print(f"File already downloaded: {f[1]}")
        else:
            if f[1] == None:
                nonelist.append(f)
            else:
                namelist.append(f)
    #download links with specified downloadname. Could be done asynchron (hard!)
    for link in namelist:
        ignorelist.append(download(link,browser,folder))
    #downloadthe links without a name sequentially
    for link in nonelist:
        ignorelist.append(download(link,browser,folder))
    #close ignorefile
    if ignorefile != None:
        for ign in ignorelist:
            if ign != None:
                file.write(ign+"\n")


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


def get_courses(browser,cleaned=True):
    #Find all availible courses and return them as list of (link,name) tuples.
    #Set cleaned to False, to get courses exactly as they are listed in ISIS
    soup = browser.get_current_page()
    #Find course names
    filter_tags = ["Meine Kurse","Alle Kurse","Kalender","Meine Startseite"]
    link_name_list = []
    for link in soup.find_all('span', class_= "media-body"):
        if not any(x in str(link) for x in filter_tags):
            if '</span>' in str(link) and '"media-body">' in str(link):
                link_name_list.append(
                str(link).split('"media-body">')[1].split("</span>")[0])
    #Find all links that lead to a course site. Order corrosponds to link names
    link_list = []
    for link in soup.find_all('a', href=True):
        if "https://isis.tu-berlin.de/course/view.php?id="in link['href']:
            if link['href'].split("view.php?id=")[1].isdigit():
                link_list.append(link['href'])
    #Clean course names if desired and return as list of (link,name) tuples
    if cleaned:
        link_name_list = [namify(i) for i in link_name_list]
    return list(zip(link_list,link_name_list))


def logout(browser):
    #End programm and logout
    logwrite("programm finished sucessfully")
    try:
        browser.open("https://isis.tu-berlin.de/login/logout.php")
        browser.select_form(
        'form[action="https://isis.tu-berlin.de/login/logout.php"]')
        browser.submit_selected()
    except:
        pass


def get_data(datafile):
    #Read data from datafile. Lines in datafile corrospond to:
    #0=username
    #1=password
    #2=subjects to be downloaded
    #3=path where course folders will be created. Use "" for current dir
    #4...=additional courses to be downloaded. Format: "<url>;;<path>"
    try:
        with open(datafile) as dfile:
            data = dfile.read().splitlines()
        if len(data) >3:
            return data
        else:
            print("wrong dataformat. Line 1 = username, 2 = password"
            +", 3=subjects to be downloaded. 4 = path to save files, use 'none'"
            +" for current dir")
            raise SystemExit
    except:
        print("unable to read datafile " + str(datafile))
        raise SystemExit

def standartrun(browser,course_list,savepath = os.getcwd()
, ignore = "isisignorefile.txt"):
    #Download all files for all courses in course_list. Representative folders
    #will be created under savepath. Links that didn't result in a pdf can be
    #safed under "ignore"

    #Reset logfile
    logwrite("",reset=True)
    #Prevent ignorefile from becoming too big
    if os.path.isfile(ignore):
        try:
            ig = open(ignore,'r')
            ig.seek(0)
            if len(ig.readlines())>80:
                ig.close()
                ig = open(ignore,'w')
                ig.close()
            else:
                ig.close()
        except:
            logwrite("unable to open ignorefile")
            exit()
    #Create course folders in savepath
    if savepath == "":
        savepath = os.getcwd()
    coursefolders = os.listdir(savepath)
    for course in course_list:
        if course[1] not in coursefolders:
            os.mkdir(os.path.join(savepath,course[1]))
    #Download all courses
    for link in course_list:
        browser.open(link[0])
        print("Starting downloads for "+link[1]+":")
        simpledownload(browser,os.path.join(savepath,link[1]),
        ignorefile= ignore)
        print("\n")
