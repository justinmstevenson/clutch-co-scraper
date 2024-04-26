from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from time import sleep
from pprint import pprint
import re
import csv

geckodriver_path = '/Users/juss_stevenson/github/clutch-co-scraper/geckodriver'
service=Service(geckodriver_path)

driver = webdriver.Firefox(service=service)
CSV_FILENAME = 'businesses_data.csv'
SITEMAP_URL = 'https://clutch.co/sitemap'
BASE_URL = 'https://clutch.co'

headers = ['id', 'data_type', 'data_title', 'data_is_paid', 'profile_link', 
           'rating', 'reviews', 'min_project_size', 'avg_hourly_rate', 
           'employees', 'location', 'service_focus', 'summary', 'website', 'url']

business_keys = {}
def scrape_first_page():
    driver.get(SITEMAP_URL)
    sleep(2)
    buttons = driver.find_elements(By.CLASS_NAME, 'sitemap-button.collapsed')
    for button in buttons:
        button.click()
        sleep(0.3)

    links = driver.find_elements(By.CSS_SELECTOR, 'div > div.sitemap-data__wrap > a')
    hrefs = [link.get_attribute('href') for link in links]
    driver.quit()
    return hrefs

def get_last_page_number():
    try:
        last_button = driver.find_element(By.CSS_SELECTOR, 'li.page-item.last a.page-link')
        return int(last_button.get_attribute('data-page'))
    except NoSuchElementException:
        print("Last page button not found.")
        return None
    
def generate_page_urls(base_url, last_page_number):
    urls = [f"{base_url}?page={page}" for page in range(1, last_page_number + 1)]
    print(f"URLS Found: {len(urls)}")
    return urls
    
def scrape_second_page(url):
    businesses_dict = {}
    driver.get(url)
    try:
        business_listings = WebDriverWait(driver, 360).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.provider-row')))
    except TimeoutException:
        driver.get(url)
        business_listings = WebDriverWait(driver, 3600).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.provider-row')))
    except Exception:
        return
    
    print(f"Scraping {url.replace(BASE_URL,'')}, {len(business_keys)} w/ {len(business_listings)} listings found /{len(business_keys)}")
    for listing in business_listings:
        try:
            business_id = listing.get_attribute('id')
            business_id = business_id.replace('provider-','').strip()
            business_id = int(business_id)
        except NoSuchElementException:
            business_id = ''
        try:
            data_type = listing.get_attribute('data-type')
            match data_type:
                case 'Sponsored': data_type = 1
                case 'featured': data_type = 2 
                case 'Directory': data_type = 3
                case _: return ''
        except NoSuchElementException:
            data_type = ''
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
            profile_link = profile_link.replace(BASE_URL,'')
        except NoSuchElementException:
            profile_link = ''
        try:
            rating = listing.find_element(By.CSS_SELECTOR, 'span.rating.sg-rating__number').text
        except NoSuchElementException:
            rating = ''
        try:
            reviews = listing.find_element(By.CSS_SELECTOR, 'a.reviews-link.sg-rating__reviews').text.strip()
            reviews = int(re.sub(r'[^0-9]', '', reviews)) #Replace all text
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
            employees = listing.find_element(By.CSS_SELECTOR, 'div[data-content*="Employees"] span').text
            employees = '(' + employees.strip().replace('+','') + ')'
        except NoSuchElementException:
            employees = ''
        try:
            location = listing.find_element(By.CSS_SELECTOR, 'div[data-content*="Location"] .locality').text.strip()
        except NoSuchElementException:
            location = ''
        try:
            ser_foc_elems = listing.find_elements(By.CSS_SELECTOR, 'div.chartAreaContainer.spm-bar-chart div.grid')
            service_focus = ', '.join([re.sub(r'<[^>]*>', '', elem.get_attribute('data-content')
                                              .strip().replace('%','% ')) for elem in ser_foc_elems])
        except NoSuchElementException:
            service_focus = ''
        try:
            summary = listing.find_element(By.CSS_SELECTOR, 'div.provider-info__description blockquote').text.strip()
        except NoSuchElementException:
            summary = ''
        try:
            website = listing.find_element(By.CSS_SELECTOR, 'div.provider-detail.col-md-2 a').get_attribute('href')
            website = re.sub(r'\?utm_source.*$', '', website)
        except NoSuchElementException:
            website = ''

        try:
            weburl = url.replace(BASE_URL,'')
        except:
            weburl = ''
        
        business = ({
            'id': business_id,
            'data_type': data_type,
            'data_title': data_title,
            'data_is_paid': data_is_paid,
            'profile_link': profile_link,
            'rating': rating,
            'reviews': reviews,
            'min_project_size': min_project_size,
            'avg_hourly_rate': avg_hourly_rate,
            'employees': employees,
            'location': location,
            'service_focus': service_focus,
            'summary': summary,
            'website': website,
            'url': weburl
        })
        business_key = business['id']
        if business_key not in business_keys:
            businesses_dict[business_key] = business
            business_keys[business_key] = business
        #pprint(business)
        #sleep(0.5)
    with open(CSV_FILENAME, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writerows(business_info for business_id, business_info in businesses_dict.items())

hrefs = scrape_first_page()
with open(CSV_FILENAME, 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader() # Write headers once

for url in hrefs:
    driver = webdriver.Firefox(service=service)
    print(f"Going to URL {url}")
    scrape_second_page(url)
    last_page_number = get_last_page_number()
    if last_page_number is not None:
        page_urls = generate_page_urls(url, last_page_number)
        for page_url in page_urls:
            scrape_second_page(page_url)
    else:
        print(f"Could not determine the last page number for URL {url}")
    driver.quit()


driver.quit()