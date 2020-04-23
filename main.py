from isisdownloader import *

print("Logging into Isis, this will take a few seconds...")
data = get_data("data.txt")
browser = setup_browser(data[0],data[1])
course_list = get_courses(browser)
print("Availible courses:")
for course in course_list:
    print(course[1])
course_list = [c for c in course_list if c[1] in
list(map(namify,data[2].split(";;")))]
print("\nOf which will be downloaded:")
for course in course_list:
    print(course[1])
print("")
standartrun(browser,course_list,savepath = data[3])
#Handle additional pages
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
