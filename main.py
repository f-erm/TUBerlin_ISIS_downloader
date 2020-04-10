from isisdownloader import *


data = get_data("data.txt")
browser = setup_browser(data[0],data[1])
course_list = get_courses(browser,ignore=data[2])
print("Availible courses:")
for course in course_list:
    print(course[1])
print("")
standartrun(browser,course_list,savepath = data[3])
counter = 4
while len(data)>counter:
    try:
        split = data[counter].split(";;")
        if not os.path.exists(split[1]):
            try:
                os.mkdir(split[1])
            except:
                print("Unable to create folder "+split[1])
        browser.open(split[0])
        simpledownload(browser,split[1])
    except:
        logwrite("Unable to download additional page: "+data[counter])
    counter += 1

###ADD YOUR CODE BELOW:###





###ADD YOUR CODE ABOVE###

logout(browser)
