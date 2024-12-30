import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np


# Base URL
base_url = "https://courses.analyticsvidhya.com/collections/courses?page="

# List to store course data
courses = {}

headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'}

# Loop through all pages
for page in range(1, 10):  # Adjust the range based on the number of pages
    page_url = base_url + str(page)
    webpage = requests.get(page_url,headers=headers).text

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(webpage, 'lxml')

    #Course title
    titles = soup.find_all('h3')[:-1]

    # Find all course links
    links = soup.find_all('a',class_="course-card course-card__public published")

    for title,link in zip(titles,links):
        courses[title.text] = 'https://courses.analyticsvidhya.com'+link['href']

def extract_course_content(link):
    webpage = requests.get(link,headers=headers).text
    course_soup = BeautifulSoup(webpage, 'html.parser')

    try:
        duration = course_soup.find_all('li',class_="text-icon__list-item")[0].text
    except:
        duration = np.nan

    try:
        rating = course_soup.find_all('li',class_="text-icon__list-item")[1].text
    except:
        rating = np.nan

    try:
        difficulty_level = course_soup.find_all('li',class_="text-icon__list-item")[0].text
    except:
        difficulty_level = np.nan

    description = ''
    for para in course_soup.find_all('div',class_="fr-view"):
        description += para.text+'\n'

    try:
        who_can_enroll = course_soup.find_all('ul',class_="checklist__list section__body")[0].text
    except:
        who_can_enroll = np.nan

    try:
        faq_ques = course_soup.find('ul',class_="faq__list section__body").find_all('strong')
        faq_ans = course_soup.find('ul',class_="faq__list section__body").find_all('p')

        faqs = ''
        for ques,ans in zip(faq_ques,faq_ans):
            faqs = faqs+'Question: '+ques.text+'\n'+'Answer: '+ans.text+'\n\n\n'
    except:
        faqs = np.nan

    try:
        takeaways = course_soup.find_all('div',class_='checklist__wrapper')[1].find_all('ul',class_="checklist__list section__body")[0].text
    except:
        takeaways = np.nan

    instructor_names = ''
    for element in course_soup.find_all('header',class_='section__headings'):
        h4_tag = element.find('h4')
        if h4_tag:
            instructor_names = instructor_names+h4_tag.text+','

    instructor_bio = ''
    for element in course_soup.find_all('div',class_='section__body'):
        instructor_bio = instructor_bio + element.text + '\n\n'

    return [duration,rating,difficulty_level,description,who_can_enroll,faqs,takeaways,instructor_names,instructor_bio]

data = []
for course_link in courses.values():
    data.append(extract_course_content(course_link))

columns= ['Duration','Course Rating','Difficulty Level','Course Description','Who Can Enroll?','FAQs','Course Takeaways','Instructors','Instructor Bio']
df = pd.DataFrame(data, columns=columns)
df.insert(0, 'Course Name', courses.keys())

# Export to Excel
output_file = "AV_Free_Courses.csv"
df.to_csv(output_file, index=False)

print(f"Data exported to {output_file} successfully.")