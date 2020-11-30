from bs4 import BeautifulSoup
from time import time
import mechanicalsoup
import os
import shutil
import re



class isisdownloader:
    '''Main part of the module, manages a mechanicalsoup browser instance and
    contains the methods to manipulate it and to find and download new files
    within ones ISIS account'''

    def __init__(self, username, password, logfile_name = None, ignorefile_name = None):
        ''' Creates browser instance, logs into isis and opens the logfile'''
        #Open browser,login and navigate to main ISIS screen
        isisurl = "https://isis.tu-berlin.de/login/index.php"
        self.browser = mechanicalsoup.StatefulBrowser()
        self.browser.open(isisurl)
        self.browser.select_form('#shibboleth_login')
        response = self.browser.submit_selected()
        self.browser.select_form('form')
        response2 = self.browser.submit_selected()
        self.browser.select_form('form')
        self.browser["j_username"] = username
        self.browser["j_password"] = password
        self.browser.submit_selected()
        #open logfile, and reset it
        try:
            self.logfile = open(logfile_name,mode = 'w')
        except:
            print("unable to open logfile")
            self.logfile = None
        #open ignorefile
        try:
            self.ignorefile = open(ignorefile_name,mode = 'a+')
            self.ignorefile.seek(0)
            self.ignorelinks = self.ignorefile.read().splitlines()
            #Prevent ignorefile from becoming too big
            if len(self.ignorelinks)>100:
                self.ignorefile.close()
                self.ignorefile = open(ignorefile_name,'w')
                self.ignorelinks = []
        except:
            print("unable to open ignorefile")
            self.ignorefile = None
            self.ignorelinks = None


    def change_to_site(self,link):
        '''Change browser instance to given link'''
        try:
            self.browser.open(link)
        except:
            print("unable to open site")
            #unable to open site. From here on out behavior would be undefined.
            exit()

    def extend_ignorelist(self,link):
        '''Adds link to ignorefile, if file is given'''
        if self.ignorefile and not self.ignorefile.closed:
            if link not in self.ignorelinks:
                self.ignorefile.write(link + "\n")


    def get_courses(self,cleaned=True):
        '''Find all availible courses and return them as list of (link,name) tuples.
        Set cleaned to False, to get courses exactly as they are listed in ISIS'''
        soup = self.browser.get_current_page()
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


    def logwrite(self,text,printit=True):
        '''Add line of text to logfile, can also be printed out'''
        text = str(text)
        if printit:
            print(text)
        if self.logfile:
            try:
                self.logfile.write(text+"\n")
            except:
                print("unable to write to logfile")


    def download(self,linktuple,folder):
        '''Download link and save as name in folder. If name = None, get new
        name. If link is not pdf it can be added to the ignorefile'''
        link = linktuple[0]
        filename = linktuple[1]
        timer = time()
        response = self.browser.open(link)
        if ".pdf" in self.browser.get_url():
            if filename == None:
            #get new name
                filename = "newfile"
                try:
                    url = self.browser.get_url()
                    filename = url.split(".pdf")[0].split("/")[-1]
                    if len(url.split('/'))>4:
                        number = url.split('/')[4]
                    else:
                        number = "no"
                        self.logwrite("link " + link + " does not contain file-id")
                    if number.isdigit():
                        filename += "_" + number
                except:
                    self.logwrite("problem with "+ link)
                    self.extend_ignorelist(link)
                #check if file already exists
                fcont = get_subfolders(folder)
                if filename in fcont or f"{filename}.pdf" in fcont:
                    print("downloaded file already exists")
                    self.extend_ignorelist(link)
            try:
                #Download file
                with open(folder+"/"+filename+".pdf", 'wb') as f:
                    f.write(response.content)
                self.logwrite("Downloaded file "+ filename + " in "
                +str(round((time()-timer),6))+ " seconds")
            except:
                self.logwrite("unable to download " + link + " " +filename)
                self.extend_ignorelist(link)
        else:
            print("file is not pdf")
            self.extend_ignorelist(link)


    def simpledownload(self,folder):
        '''Download all pdf's on current page and save them in folder. Ignorefile
        can be uses to save links, not resulting in a pdf, for the next run.'''
        if not os.path.exists(folder):
            raise Exception("folder does not exist")
        soup = self.browser.get_current_page()
        linklist = []
        print("found links:")
        #Get all links on current site as (link,name) and filter for keywords
        filterout = ["login","logout","lang=","/quiz/","/forum/","/calendar/",
        "/admin/","/grade/","/local/","/etherpadlite/","/user/","/enrol/",
        "/message/","/course/view.php?id=","/assign/","/choicegroup/",
        "/recent.php?id","/questionnaire/","/glossary/","/videoservice/"]
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
        if self.ignorelinks != None:
            for entry in list(linklist):
                if entry[0] in self.ignorelinks:
                    linklist.remove(entry)
        #Display all found links
        for i in linklist:
            print(i)
        print("\n")
        #get already downloaded files
        foldercontent=get_subfolders(folder)
        #download the files, if they are new
        for f in linklist:
            if f[1] in foldercontent or f"{f[1]}.pdf" in foldercontent:
                print(f"File already downloaded: {f[1]}")
            else:
                self.download(f,folder)


    def standartrun(self,course_list,savepath = None):
        '''Download all files for all courses in course_list. Representative
        folders will be created under savepath.'''
        #Create course folders in savepath
        if savepath == "none":
            savepath = os.getcwd()
        coursefolders = os.listdir(savepath)
        for course in course_list:
            if course[1] not in coursefolders:
                os.mkdir(os.path.join(savepath,course[1]))
        #Download all courses
        for link in course_list:
            self.change_to_site(link[0])
            print("Starting downloads for "+link[1]+":")
            try:
                self.simpledownload(os.path.join(savepath,link[1]))
            except:
                self.logwrite(f"unable to download {link[1]}")
            print("\n")


    def end(self):
        '''End instance by logging out and closing all open files'''
        try:
            self.browser.open("https://isis.tu-berlin.de/login/logout.php")
            self.browser.select_form(
            'form[action="https://isis.tu-berlin.de/login/logout.php"]')
            self.browser.submit_selected()
        except:
            pass
        finally:
            self.logwrite("programm finished sucessfully",False)
            if self.logfile:
                self.logfile.close()
            if self.ignorefile:
                self.ignorefile.close()


### END OF CLASS. THE FOLLOWING ARE SUPLEMENTARY METHODS ###


def get_data(datafile):
    '''Read data from datafile. Lines in datafile corrospond to:
    0 = username
    1 = password
    2 = subjects to be downloaded
    3 = path where course folders will be created. Use "" for current dir
    4 = ingorefile_name or 'none' if not wanted
    5...= additional courses to be downloaded. Format: "<url>;;<path>"
    Returns Data if sucessfull, None otherwise'''
    try:
        with open(datafile) as dfile:
            data = dfile.read().splitlines()
        if len(data) >4:
            data[2]=data[2].split(';;')
            if data[3] == "none":
                data[3] = None
            if data[4] == "none":
                data[4] = None
            return data
        else:
            raise Exception("unable to open datafile")
    except:
        raise Exception("unable to open datafile")


def namify(name):
    '''Turn string into a viable filename'''
    valid ="-_() abcdefghijklmnopqrstuvwxyzöäü"\
    "ABCDEFGHIJKLMNOPQRSTUVWXYZÖÄÜ0123456789"
    filename = ''.join(c for c in name if c in valid)
    pattern = re.compile(r'\s+')
    filename = re.sub(pattern, '_', filename)
    return filename


def get_name_from_tag(tag):
    '''Take html tag, if isis displays it as a name, return that name. Otherwise
    return None.'''
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
    '''Moves all files from src to dst, whose names contain >= 1
    of the terms in list'''
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
        print(f"path is not valid. src:{str(scr)} dst: {str(dst)}")


def get_subfolders(folder):
    '''Return content of folder and and all its subfolders'''
    list = []
    list.extend([f for f in os.listdir(folder)
    if os.path.isfile(os.path.join(folder,f))])
    for sub in [d for d in os.listdir(folder)
    if os.path.isdir(os.path.join(folder, d))]:
        list.extend(get_subfolders(os.path.join(folder,sub)))
    return list
