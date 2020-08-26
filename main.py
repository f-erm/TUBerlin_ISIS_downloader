from isisdownloader import *

if __name__ == "__main__":
    logfile_name = "isislog.txt"

    #Setup
    print("Logging into Isis, this will take a few seconds...")
    try:
        data = get_data("data.txt")
    except:
        print("unable to open datafile. Run setup.py to fix your Datafile")
        exit()
    downloader = isisdownloader(data[0],data[1],logfile_name,data[4])

    #Show and filter the courses
    course_list = downloader.get_courses(cleaned=False)
    course_list = [c for c in course_list if c[1] in data[2]]
    print("Courses to be downloaded:")
    for course in course_list:
        print(namify(course[1]))

    #Download the courses
    downloader.standartrun(course_list,savepath = data[3])

    #Handle additional pages
    for c in data[5:]:
        try:
            split = c.split(";;")
            if not os.path.exists(split[1]):
                    os.mkdir(split[1])
            downloader.change_to_site(split[0])
            downloader.simpledownload(browser,split[1])

        except:
            downloader.logwrite("Unable to download additional page: "+c)

    #end
    downloader.end()
    print("Logs: ")
    with open(logfile_name,mode='r') as file:
        for line in file.read().splitlines():
            print(line)
