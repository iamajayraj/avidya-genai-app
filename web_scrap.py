import requests
from bs4 import BeautifulSoup

# Base URL
base_url = "https://courses.analyticsvidhya.com/collections/courses?page="

# Headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'}


def course_links(base_url):
    # List to store course data
    courses = []
    # Loop through all pages
    for page in range(1, 10):  # Adjust the range based on the number of pages
        page_url = base_url + str(page)
        webpage = requests.get(page_url, headers=headers).text

        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(webpage, 'lxml')

        # Find all course links
        links = soup.find_all('a', class_="course-card course-card__public published")

        for link in links:
            courses.append('https://courses.analyticsvidhya.com' + link['href'])

        return courses

