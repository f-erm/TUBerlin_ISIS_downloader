##### TU-Berlin Isis-downloader

---


## INTRODUCTION
  Hello and welcome to the the Isis-downloader, designed to automate the daily
  download of your lecture scripts and assignments. This script will automatically
  log into your TU_Berlin ISIS account, get all the courses your are subscribed to,
  check which files you have already downloaded and download the rest. Read the
  Setup section below to learn how to set it up.


## IMPORTANT!!!
This is a private project which does in no way represent the TU-Berlin.
By using this code you take on full responsibility for any sort of resulting
damages.


## DEPENDENCIES
  To run this script you'll need to install the modules 'bs4' and 'mechanicalsoup'.
  Use pip install <module> to install them.


## SETUP
  Start by running "setup.py". It will setup a datafile, containing your login
  data and personal preferences (e.g what courses you want to be downloaded).
  By default this script will check every courses mainpage and download the
  missing files. Since some courses place their files on seperate pages,
  you might have to add those pages yourself. Setup.py will ask you wether you
  want to do that, all you have to do is follow its instructions. You will
  need the URL of the page you want to be checked and a folder, where you want
  the files to be stored. It is advised to add these options later on.
  Run setup.py again to change any settings you have made. If you want to,
  you can modify the script yourself. To learn how to do it, the scripts
  functions are documented below. After each run you will find a summary of it
  in new file called "isislog.txt". Once you are ready, run main.py to start
  downloading.

  IMPORTANT: As of now, renaming the downloaded files is not supported, and will
  lead to duplicates!!


## DOCUMENTATION

    -isisdownloader(username, password, logfile_name = None, ignorefile_name = None)
      Creates the browser instance, which is needed to execute the scripts
      functions. Since you can only see your ISIS courses while loged in, your
      TUBit username and password are needed to log you in. Also opens and manages
      the logfile and ignorefile. Use "None" as their arguments if you do not wish
      to use them.
      E.g My_downloader = isisdownloader(myname, mypw, "logs.txt", "ignore.txt")

      Contains the methods:

        -get_courses(cleaned=True):
          Gets all the courses you are subscribed to. By default the returned
          course names will be modifyed, so they can be used to name folders
          after them. Set cleaned to False to get the names as displayed in ISIS.
          E.g: course_list = My_downloader.get_courses(True)

        -standartrun(course_list,savepath = None)
          Takes courselist (created by get_courses) and savepath (current dir by default)
          as arguments. Downloads all new files and saves them in folders, named
          after the course. The folders are created under savepath. If the folders
          already exist, it will check which files are in there, to only download
          E.g: My_downloader.standartrun(course_list, savepath = "/home/user/")

        -change_to_site(link)
          opens the link with the browser instance. Used to navigate within ISIS.
          E.g: My_downloader.change_to_site("www.tu.berlin")

        -simpledownload(folder):
          Download all files on current browser page and save them in folder (given as path).
          Use change_to_site to change to the page you want to checkout. If a
          ignorefile is given, all links not resulting in a pdf will be saved there,
          and won't be checked in future runs.
          E.g: My_downloader.change_to_site("https://isis.tu-berlin.de/mod/folder/view.php?id=757931")
               My_downloader.simpledownload("/home/user/")

        -end():
          Logs out of ISIS and closes the open files (log and ignore). Use it before
          you discard your downloader instance.
          E.g My_downloader.end()

    -get_data(datafile):
      Your login data and settings need to be stored somewhere. This is done in a txt
      file, its path beeing the the argument for this function. Each line of the file
      is reseved for a specific argument.
      line 1: put your username here
      line 2: put your password here
      line 3: put the courses you want to be downloaded here, seperated by ','.
              Use exactly the same name as ISIS.
      line 4: put the path, where you want your coursefolders to be created, here.
              If you want the current directory, use "none"
      line 5: put the path of your ignorefile here. If you do not want to cash
              links not resutling in a .pdf, just use "none"
      line 6  and onwards: Add any additional pages you want to be checked here.
              Use format "<url>;;<path to where you want to store your files>"
      Example for a datafile:
            "
            myname
            mypassword
            [SoSe 2020] ISDA;;StochServSS2020;;SPR20;;[2020-SS] AlgoDat
            none
            none
            https://isis.tu-berlin.de/mod/folder/view.php?id=757931;;/home/user/projects/
            "

    -movefiles(src,dst,list):
      You may want to sort your files even further. This function is included to help
      you. It will move all files from src to dst (both given as path), whose names
      contain at least one of the terms given in list. One possible usecase would be
      to move all assignments to a seperate folder.
      IMPORTANT: To be recognized by the script the files still need to be inside
      their designated coursefolders. You can create as many subfolders in there as
      you want and move your files to any of them, as long as they stay inside their
      coursefolder
      E.g: movefiles("/home/user/","/home/user/assignments",["Übung","Aufgabe","TUT"])


## ABOUT THE BOT
  This script includes a telegram-bot to notify you about new downloaded files.
  Since this script is intended to be run remotely, this can come in handy.
  Just open the telegram_bot folder and follow the instructions to set it up.
  Use it to send yourself the contents of isislog.txt


## THIS IS A WORK IN PROGRESS
  Possible issues:

    -Since every course uses a different scheme to name its files, some courses
      might be unable to find a name for their files, forcing the script to download
      every single file in that course, every time it is executed. This will result
      in significant delays.
      Currently tested and working on:
      Info-Prop,Ana1fIng WS2019/20, LinAlg WS201920, WS 19/20 IntroProg,
      ROrg WS 19/20, [19/20 WiSe] FoSA, [2020-SS] AlgoDat, StochServSS2020, SPR20

    -PDFs are the only supported file type. While other formats lke .txt could
    be added later on, there won't be any support for video files, as they are simply
    too large for the scripts method of downloading.

    -Given the way the sript handles duplicates, it is not possible to rename files.
    This could be added in the future, but might cause some unforeseen problems.
