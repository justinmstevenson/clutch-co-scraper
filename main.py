from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from time import sleep
from pprint import pprint
import csv


# Set the path to the GeckoDriver executable
geckodriver_path = '/Users/juss_stevenson/github/clutch-co-scraper/geckodriver'  # Replace with the actual path
service=Service(geckodriver_path)
# Initialize the Firefox driver
driver = webdriver.Firefox(service=service)
CSV_FILENAME = 'businesses_data.csv'
SITEMAP_URL = 'https://clutch.co/sitemap'
headers = [
    'id',
    'data_type',
    'class',
    'data_title',
    'data_is_paid',
    'profile_link',
    'company_name',
    'rating',
    'reviews',
    'min_project_size',
    'avg_hourly_rate',
    'employees',
    'location',
    'service_focus',
    'summary',
    'website'
]

businesses_data = []

def scrape_first_page(driver):
    driver.get(SITEMAP_URL)
    sleep(3)
    buttons = driver.find_elements(By.CLASS_NAME, 'sitemap-button.collapsed')
    for button in buttons:
        button.click()
        sleep(0.5)

    links = driver.find_elements(By.CSS_SELECTOR, 'div > div.sitemap-data__wrap > a')
    hrefs = [link.get_attribute('href') for link in links]
    return hrefs

def write_business_to_csv(business_data, headers, mode='a'):
    with open(CSV_FILENAME, mode, newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        if file.tell() == 0:  # Check if the file is empty to write headers
            writer.writeheader()
        writer.writerow(business_data)

def go_to_next_page():
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, 'li.page-item.next a.page-link')
        next_button.click()
        return True
    except NoSuchElementException:
        return False
    
def scrape_businesses(url):
    driver.get(url)
    business_listings = driver.find_elements(By.CSS_SELECTOR, 'li.provider-row')
    for listing in business_listings:
        try:
            business_id = listing.get_attribute('id')
        except NoSuchElementException:
            business_id = ''
        try:
            data_type = listing.get_attribute('data-type')
        except NoSuchElementException:
            data_type = ''
        try:
            class_name = listing.get_attribute('class')
        except NoSuchElementException:
            class_name = ''
        try:
            data_title = listing.get_attribute('data-title')
        except NoSuchElementException:
            data_title = ''
        try:
            data_is_paid = listing.get_attribute('data-is-paid')
        except NoSuchElementException:
            data_is_paid = ''
        try:
            profile_link = listing.find_element(By.CSS_SELECTOR, 'a[href*="/profile"]').get_attribute('href')
        except NoSuchElementException:
            profile_link = ''
        try:
            company_name = listing.find_element(By.CSS_SELECTOR, 'p.company_info_wrap_tagline').text
        except NoSuchElementException:
            company_name = ''
        try:
            rating = listing.find_element(By.CSS_SELECTOR, 'span.rating.sg-rating__number').text
        except NoSuchElementException:
            rating = ''
        try:
            reviews = listing.find_element(By.CSS_SELECTOR, 'a.reviews-link.sg-rating__reviews').text.strip()
        except NoSuchElementException:
            reviews = ''
        try:
            min_project_size = listing.find_element(By.CSS_SELECTOR, 'div[data-content*="Min. project size"] span').text.strip()
        except NoSuchElementException:
            min_project_size = ''
        try:
            avg_hourly_rate = listing.find_element(By.CSS_SELECTOR, 'div[data-content*="Avg. hourly rate"] span').text.strip()
        except NoSuchElementException:
            avg_hourly_rate = ''
        try:
            employees = listing.find_element(By.CSS_SELECTOR, 'div[data-content*="Employees"] span').text.strip()
        except NoSuchElementException:
            employees = ''
        try:
            location = listing.find_element(By.CSS_SELECTOR, 'div[data-content*="Location"] .locality').text.strip()
        except NoSuchElementException:
            location = ''
        try:
            service_focus_elements = listing.find_elements(By.CSS_SELECTOR, 'div.chartAreaContainer.spm-bar-chart div.grid')
            service_focus = [{'service': elem.get_attribute('data-content').split('<b>')[-1].split('</b>')[0], 'percentage': elem.get_attribute('data-content').split('<i>')[-1].split('</i>')[0]} for elem in service_focus_elements]
        except NoSuchElementException:
            service_focus = []
        try:
            summary = listing.find_element(By.CSS_SELECTOR, 'div.provider-info__description blockquote').text.strip()
        except NoSuchElementException:
            summary = ''
        try:
            website = listing.find_element(By.CSS_SELECTOR, 'div.provider-detail.col-md-2 a').get_attribute('href')
        except NoSuchElementException:
            website = ''

        # Append the parsed data to the businesses_data list
        businesses_data.append({
            'id': business_id,
            'data_type': data_type,
            'class': class_name,
            'data_title': data_title,
            'data_is_paid': data_is_paid,
            'profile_link': profile_link,
            'company_name': company_name,
            'rating': rating,
            'reviews': reviews,
            'min_project_size': min_project_size,
            'avg_hourly_rate': avg_hourly_rate,
            'employees': employees,
            'location': location,
            'service_focus': service_focus,
            'summary': summary,
            'website': website
        })
        for business in businesses_data:
            write_business_to_csv(business, headers)

hrefs = scrape_first_page()
write_business_to_csv({}, headers, mode='w')

for url in hrefs:
    while True:
        new_data = scrape_businesses(url)
        if new_data:  # Check if new_data is not None or empty
            businesses_data.extend(new_data)
        else:
            continue  # If no data is returned, exit the loop
        if not go_to_next_page():
            continue
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li.provider-row')))

    # Print the array for testing
write_business_to_csv(businesses_data, 'businesses_data.csv')