from console import loggable
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from data import WebData

# Will be driver instance later on
driver = None

@loggable
def input_email(email: str) -> None:
    """inputs email into the 'Email address' field on Salad's login page."""
    global driver

    def load_loginpage() -> None:
        """loads chrome driver and redirects to https://salad.com/login"""
        print('opening salad login page')
        
        global driver

        url = "https://salad.com/login"
        driver_options = Options()
        driver = webdriver.Chrome(options = driver_options)  # Redirect log to null
        driver.minimize_window() # need fix for this

        # Load login page
        driver.get(url = url)
        WebDriverWait(driver, 30).until(EC.url_matches(pattern = url))

    def enter_email(email):
        #os.system('cls')
        print("[ Salad Login ]")
        print('  - entering email')
        email_element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, 'email-input')))
        email_element.send_keys(email)
        time.sleep(1)

    def agree_tos():
        print('  - checking tos checkbox')
        tos_checkbox = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//label[@class="is-clickable"]/input')))
        tos_checkbox.click()
        time.sleep(1)

    def login_button():
        print('  - pressing login button')
        login_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//button[@class="css-187tor3 e1mpl7cw11"]')))
        login_button.click()
        time.sleep(1)
        
        auth_code = input('  - 2fa code: ')
        print('  - entering 2fa code')
        auth_code_textbox = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, 'code-input')))
        auth_code_textbox.send_keys(auth_code)
        time.sleep(1)
        print('  - pressing submit button')
        submit_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//button[@class="css-187tor3 e1mpl7cw11"]')))
        submit_button.click()
        time.sleep(1)

    def fix_redirect():
        print('  - fixing redirects')
        url = "https://salad.com/earn/summary"

        for _ in range(2):
            driver.get(url = url)
            WebDriverWait(driver, 30).until(EC.url_to_be(url))
            time.sleep(1)

        print('  - login successful')

    def scrape_stats() -> tuple:
        os.system('cls')
        print('  - scraping stats from webpage')

        current_balance_xpath = '//*[@id="root"]/div/div[2]/div[2]/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/div[2]'
        lifetime_balance_xpath = '//*[@id="root"]/div/div[2]/div[2]/div[1]/div/div[1]/div/div[1]/div[2]/div[2]/div[2]'

        while True:
            current_balance = float(WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, current_balance_xpath))).text.replace('$', ''))
            lifetime_balance = float(WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, lifetime_balance_xpath))).text.replace('$', ''))


            WebData.CURRENT_BALANCE = current_balance
            WebData.LIFETIME_BALANCE = lifetime_balance

            # redeem start here
            pass
        
            time.sleep(1)

    load_loginpage()
    enter_email(email = email)
    agree_tos()
    login_button()
    fix_redirect()
    scrape_stats()