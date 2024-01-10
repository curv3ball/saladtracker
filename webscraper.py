from console import loggable, log
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from data import WebData, Globals, Settings
from datetime import datetime

# Will be driver instance later on
driver = None

@loggable
def input_email(email: str) -> None:
    """inputs email into the 'Email address' field on Salad's login page."""
    global driver

    def load_loginpage() -> None:
        """loads chrome driver and redirects to https://salad.com/login"""
        if Settings.DEBUG:
            log('opening salad login page')
        
        global driver

        url = "https://salad.com/login"
        driver_options = Options()
        driver = webdriver.Chrome(options = driver_options)  # Redirect log to null
        driver.minimize_window() # need fix for this

        # Load login page
        driver.get(url = url)
        WebDriverWait(driver, 30).until(EC.url_matches(pattern = url))

    def enter_email(email):
        if Settings.DEBUG:
            log("[ Salad Login ] => entering email", clear = True)
        email_element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, 'email-input')))
        email_element.send_keys(email)
        time.sleep(1)

    def agree_tos():
        if Settings.DEBUG:
            log('[ Salad Login ] => checking tos checkbox')
        tos_checkbox = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//label[@class="is-clickable"]/input')))
        tos_checkbox.click()
        time.sleep(1)

    def login_button():
        if Settings.DEBUG:
            log('[ Salad Login ] => pressing login button')
        login_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//button[@class="css-187tor3 e1mpl7cw11"]')))
        login_button.click()
        time.sleep(1)
        
        auth_code = input('[ Salad Login ] => 2fa code: ')
        if Settings.DEBUG:
            log('[ Salad Login ] => entering 2fa code')
        auth_code_textbox = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, 'code-input')))
        auth_code_textbox.send_keys(auth_code)
        time.sleep(1)
        
        if Settings.DEBUG:
            log('[ Salad Login ] => ressing submit button')
        submit_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//button[@class="css-187tor3 e1mpl7cw11"]')))
        submit_button.click()
        time.sleep(1)

    def fix_redirect():
        if Settings.DEBUG:
            log('[ Salad Login ] => fixing redirects')
        url = "https://salad.com/earn/summary"

        for _ in range(2):
            driver.get(url = url)
            WebDriverWait(driver, 30).until(EC.url_to_be(url))
            time.sleep(1)

        log('[ Salad Login ] => login successful')

    def scrape_stats() -> tuple:
        if Settings.DEBUG:
            log('[ Salad Login ] => scraping stats from webpage')

        current_balance_xpath = '//*[@id="root"]/div/div[2]/div[2]/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/div[2]'

        Globals.SCRIPT_START_TIME = datetime.now()

        while True:
            current_balance = float(WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, current_balance_xpath))).text.replace('$', ''))

            WebData.CURRENT_BALANCE = current_balance
            
            if Settings.DEBUG:
                log(f"[ WebDriver ] => Current Balance:    {WebData.CURRENT_BALANCE}\nUptime:             {Globals.SCRIPT_UP_TIME}", clear = True)

            time.sleep(1)

    load_loginpage()
    enter_email(email = email)
    agree_tos()
    login_button()
    fix_redirect()
    scrape_stats()