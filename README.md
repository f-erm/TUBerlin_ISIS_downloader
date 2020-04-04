#INTRODUCTION
  Hello and welcome to the the Isis-downloader, designed to automate the daily
  download of your lecture scripts and assignments. This script will automatically
  log into your TU_Berlin ISIS account, get all the courses your are subscribed to,
  check which files you have already downloaded and download the rest. Read the
  documentation to learn how to set it up.


#DEPENDENCIES
  To run this script you'll need to install the modules 'bs4' and 'mechanicalsoup'.
  Use pip install <module> to install them.


#DOCUMENTATION
  By default this script will check every courses mainpage and download the missing
  files. Since some courses place their files on seperate pages
  (e.g 'Rechnerorganisations' placing its lecture scripts under
  ...mod/folder/view.php?id=731755 instead of its mainpage), you might have to
  modify the script yourself, designated place can be found at the bottom of the
  script. To learn how to do it, the scripts functions are documented below.
  After each run you will find a summary of it in new file called "isislog.txt"
  IMPORTANT: You will need to creat a "data.txt" file, containing information
  such as your TUBit username and password, as the script won't be able to
  log into your ISIS account without it. Checkout 'get_data()' below to learn how.

    -setup_browser(username,password):
      Creates the browser instance, which is needed to execute the scripts
      functions. Since you can only see your ISIS courses while loged in, your
      TUBit username and password are needed to log you in.
      E.g: browser = setup_browser("<myname>","<mypassword>")

    -get_courses(browser,ignore = []):
      Take a browser object and get all the courses you are subscribed to. If you
      want to exclude some courses (e.g. "EECS-Studium"), set ignore to a list,
      containing their names (exactly as displayed in ISIS) as strings.
      E.g: course_list = get_courses(<browserinstance>,ignore = ["EECS-Studium","Info-Prop"])

    -get_data(datafile):
      Your login data and settings need to be stored somewhere. This is done in a txt
      file, its path beeing the the argument for this function. Each line of the file
      is reseved for a specific argument.
      line 1: put your username here
      line 2: put your password here
      line 3: put the courses you do not want to be check here, seperated by ','.
              Use exactly the same name as ISIS.
              If you want all availible courses, input "none"
      line 4: put the path, where you want your coursefolders to be created, here.
              If you want the current directory, just type "none"
      Example for a datafile:
            "
            myname
            mypassword
            none
            none
            "

    -standartrun(browser,course_list,savepath = os.getcwd(), ignore = "isisignorefile.txt")
      Takes browser and courselist (created by get_courses) as arguments. Downloads
      all new files and saves them in folders, named after the course. The folders
      are created under savepath. If savepath is not specified, they are created
      in the current directory. If the folders already exist, it will check which
      files are in there, to only download the new files. To speed up the process,
      a new file called "isisignorefile.txt" in which all not in a pdf file resulting
      links are saved, will be created. If you do not want that, set "ignore" to "none".
      E.g: standartrun(browser,course_list, savepath = "/home/user/", ignore = "none")

    -simpledownload(browser,folder,format=None,ignorefile='none'):
      Download all files on current browser page and save them in folder (given as path).
      If you want to speedup the process, you can again specify a ignorefile.
      For some courses it might be helpful to specify a format, so only links containing
      said format will be downloaded
      (e.g "https://isis.tu-berlin.de/mod/resource/view.php?id=").
      Use browser.open(<url>) to change to the page you want to checkout.
      E.g: browser.open("https://isis.tu-berlin.de/mod/folder/view.php?id=757931")
           simpledownload(browser,"/home/user/",ignorefile = "isisignorefile.txt")

    -movefiles(src,dst,list):
      You may want to sort your files even further. This function is included to help
      you. It will move all files from src to dst (both given as path), whose names
      contain at least one of the terms given in list. One possible usecase would be
      to move all assignments to a seperate folder.
      E.g: movefiles("/home/user/","/home/user/assignments",["Übung","Aufgabe","TUT"])


#ABOUT THE BOT
  This script includes a telegram-bot to notify you about new downloaded files.
  Since this script is intended to be run remotely, this can come in handy.
  Just open the telegram_bot folder and follow the instructions to set it up.
  Use it to send yourself the contents of isislog.txt


#THIS IS A WORK IN PROGRESS
  Possible issues:
    -Since every course uses a different scheme to name its files, some courses
    might be unable to find a name for their files, forcing the script to download
    every single file in that course, every time it is executed. This will result
    in significant delays.
    Currently tested and working on:
    Info-Prop,Ana1fIng WS2019/20, LinAlg WS201920, WS 19/20 IntroProg, ROrg WS 19/20, [19/20 WiSe] FoSA
  -Planned features:
    -Currently, PDFs are the only supported file type. Given recent developments,
    Video files will be more prevalent soon, so support for MP4 and other formats
    is needed
    -To make the script more accessible for those without programming knowledge,
    a small setup script would be neat.
