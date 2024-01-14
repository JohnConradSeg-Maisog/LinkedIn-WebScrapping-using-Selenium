from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException
from time import sleep
import pandas as pd
import logging
import random

### Log-in to LinkedIn
def login(email, password):
    driver.find_element(By.ID, 'session_key').send_keys(email); wait()
    driver.find_element(By.ID, 'session_password').send_keys(password); wait()
    driver.find_element(By.XPATH, '//*[@type="submit"]').click();wait()

### Seconds to wait
def wait():
    sleep(random.uniform(2.5,5))

### Wait to load elements
def element_wait(by, text):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((by, text)))
    except TimeoutException:
        logging.debug("Element not found.")
        pass

### Scroll to and click job
def scroll_to(job_list_item):
    driver.execute_script("arguments[0].scrollIntoView(true);", job_list_item)
    job_list_item.click()

### Get element value
def get_element(by, text):
    try:
        elementValue = driver.find_element(by, text).text
        return elementValue
    except NoSuchElementException:
        return ""

### Get list of skills
def get_skills():
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//a[starts-with(text(), "Skills:")]')))

    except (NoSuchElementException, TimeoutException):
        return ""
    
    driver.find_element(By.XPATH, '//a[starts-with(text(), "Skills:")]').click(); wait()
    driver.find_element(By.XPATH, '//span[text()="Show all skills"]').click(); wait()
    skills = driver.find_elements(By.XPATH, '//ul[@class="job-details-skill-match-status-list"]//li')
    jobSkills = ""
    for skill in skills:
        jobSkills += skill.text + ","
    driver.find_element(By.XPATH, '//button[@aria-label="Dismiss"]').click(); wait()
    return jobSkills


### Save df into csv
def save_file(df, pageNumber):
    print("Saved file.")
    df.to_csv(f'LinkedIn {jobTitle} Recent Job Postings_Page{pageNumber}.csv', index=False)

### Main function
def begin_scrape(jobTitle):
    ### Create dataframe to store jobs
    df_jobs = pd.DataFrame(columns=['Title', 'CompanyDetails', 'JobDetails', 'JobDescription', 'JobSkills'])
    driver.get("https://www.linkedin.com/jobs/"); wait()
    element_wait(By.CLASS_NAME, 'jobs-search-box__text-input')
    driver.find_element(By.CLASS_NAME, 'jobs-search-box__text-input').send_keys(jobTitle + Keys.ENTER); wait()
    for page in range(2, 50):
        jobs = driver.find_elements(By.CLASS_NAME, "occludable-update")
        for job in jobs:
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", job)
                job.click(); wait()
                jobName = get_element(By.CLASS_NAME, "job-details-jobs-unified-top-card__job-title-link")
                companyDetails = get_element(By.XPATH, '//div[@class="job-details-jobs-unified-top-card__primary-description-without-tagline mb2"]')
                jobDetails = get_element(By.XPATH, '//div[@class="mt3 mb2"]/ul/li[1]')
                jobDescription = get_element(By.CLASS_NAME, "jobs-description__content")
                print("Job Name: ", jobName)
                jobSkills = get_skills()
                new_job = pd.DataFrame({'Title': [jobName],
                                    'CompanyDetails': [companyDetails],
                                    'JobDetails': [jobDetails],
                                    'JobDescription': [jobDescription],
                                    'JobSkills': [jobSkills]})
                df_jobs = pd.concat([df_jobs, new_job], ignore_index=True)
            except (ElementNotInteractableException, StaleElementReferenceException):
                pass
        print("Saved 25 jobs.")
        save_file(df_jobs, page - 1)
        df_jobs = df_jobs[0:0]
        driver.find_element(By.XPATH,f"//button[@aria-label='Page {page}']").click();wait()


### Chrome Drive Setup
PATH = "/Users/johnconradsegmaisog/Documents/Work Portfolio/LinkedIn WebScrapping with Selenium/chromedriver"
driver = webdriver.Chrome(service=Service(executable_path=PATH))
driver.get("https://www.linkedin.com")
driver.maximize_window()

### Login details
email = 'emailhere'
password = 'passwordhere'
login(email, password)

sleep(20)

### Search Job Name
jobTitle = "Data Analyst"

### Start scraping
begin_scrape(jobTitle)