from os import system
import ctypes
import time
import sys
import psutil
from dearpygui import dearpygui
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchWindowException
from widgets import Widgets
from init import window_settings

class Console:
    @staticmethod
    def clear() -> None:
        """clears the console window"""
        system("cls")

    @staticmethod
    def hide() -> None:
        """hides the console window"""
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        user32 = ctypes.WinDLL('user32', use_last_error=True)

        window_handle = kernel32.GetConsoleWindow()

        if window_handle:
            user32.ShowWindow(window_handle, 0)
            kernel32.CloseHandle(window_handle)

    @staticmethod
    def workload_type() -> str:
        """returns the salad workload type"""
        for process in psutil.process_iter(['pid', 'name']):
            if psutil.pid_exists(process.info['pid']):
                process_name = process.info['name']
                if process_name == "vmmem":
                    return "Container"
                elif process_name == "t-rex.exe":
                    return "T-Rex"
                elif process_name == "xmrig":
                    return "XMRig"
        return "Unknown"

class WebScraper:
    driver = None

    @staticmethod
    def load_login_page(email: str) -> None:
        """loads chrome driver and redirects to https://salad.com/login"""
        print("loading login page")

        url = "https://salad.com/login"
        browser_options = Options()
        WebScraper.driver = webdriver.Chrome(options=browser_options)
        WebScraper.driver.minimize_window() # uncomment this when actually release

        try:
            WebScraper.driver.get(url)
            WebScraper.input_email(email)
        except Exception:
            print("falied to open the login page, close program and try again")
            sys.exit()

    @staticmethod
    def input_email(email: str) -> None:
        """fills out email, accepts tos and logs in"""
        print("loading login page")
        try:
            # enter email
            email_element = WebDriverWait(WebScraper.driver, 10).until(EC.presence_of_element_located((By.ID, 'email-input')))
            email_element.send_keys(email)
            time.sleep(1)

            # click agree to tos checkbox
            tos_checkbox = WebDriverWait(WebScraper.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//label[@class="checkbox"]/input')))
            tos_checkbox.click()
            time.sleep(1)

            # press login button
            login_button = WebDriverWait(WebScraper.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[@class="button is-primary"]')))
            login_button.click()
            time.sleep(1)
        except Exception:
            print("failed inputting email, close program and try again")
            sys.exit()

        # update the labels to prepare for auth
        try:
            dearpygui.set_value("label_email", "Verification code (check email)")
            dearpygui.set_value("textbox_email", "")
            Conditions.AWAITING_AUTH = True
            time.sleep(0.5)
        except Exception:
            print("error updating labels to auth mode")
            sys.exit()

    @staticmethod
    def verify_email(auth_code: str) -> None:
        """inputs auth code after user types it"""
        print("identifying auth page")
        try:
            # enter 2fa code
            code_input = WebDriverWait(WebScraper.driver, 10).until(EC.presence_of_element_located((By.ID, 'code-input')))
            code_input.send_keys(auth_code)
            time.sleep(2)

            # press login button
            login_button = WebDriverWait(WebScraper.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[@class="button is-primary"]')))
            login_button.click()
            time.sleep(2)
            WebScraper.fix_reirect()
        except NoSuchWindowException as e:
            print(f"error locating auth page, close program and try again [{type(e).__name__}]")
            sys.exit()

    @staticmethod
    def fix_reirect() -> None:
        """redirect workaround for salad's website"""
        print("attempting redirect")
        url = "https://salad.com/earn/summary"
        try:
            WebScraper.driver.get(url)
            WebDriverWait(WebScraper.driver, 10).until(EC.url_to_be(url))
            time.sleep(1)
            WebScraper.driver.get(url)
            time.sleep(1)
            WebScraper.scrape_stats()
        except Exception as e:
            print(f"error redirecting to summary page, close program and try again\n{e}\n")

    @staticmethod
    def scrape_stats() -> None:
        """scrapes chopping stats from https://salad.com/summary"""
        Console.clear()
        print("scraping stats from /summary")
        # remove old widgets
        dearpygui.delete_item("label_email")
        dearpygui.delete_item("textbox_email")
        dearpygui.delete_item("button_login")

        cb = None
        mh = None
        #lb = None
        #rr = None
        start_time = time.time()

        imgui = Widgets()
        imgui.label("Elapsed Time: 0s", "label_updates")
        # do something with the data, figure out how to plot it maybe would be cool
        with dearpygui.table(header_row=True, policy=dearpygui.mvTable_SizingFixedFit, no_host_extendX=False,
            borders_innerV=True, delay_search=True, borders_outerV=True, borders_innerH=True,
            borders_outerH=True, parent=window_settings.WINDOW_TAG, tag="table_stats"):

            dearpygui.add_table_column(label="Hours", width_stretch=True)
            dearpygui.add_table_column(label="Workload", width_stretch=True)
            dearpygui.add_table_column(label="Balance", width_stretch=True)

            while True:
                try:
                    summary_div = WebDriverWait(WebScraper.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'c0111')))
                    WebDriverWait(WebScraper.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'c0114')))

                    elements = summary_div.find_elements(By.CLASS_NAME, 'c0114')

                    for element in elements:
                        label = element.find_element(By.CLASS_NAME, 'c0115').text
                        value = element.find_element(By.CLASS_NAME, 'c0116').text
                        if "current balance" in label.lower():
                            cb = value
                        elif "lifetime balance" in label.lower():
                            lb = f"{float(value.replace("$", "").replace(",", "")):.2f}"
                        elif "total chopping hours" in label.lower():
                            mh = value.replace(" hours", "")
                        elif "number of rewards redeemed" in label.lower():
                            rr = value.replace(" rewards", "").replace(" reward", "")
                        else:
                            print(f"error getting stats for ['{label}', '{value}']")

                    cf = Console.workload_type()

                    if dearpygui.does_item_exist("table_stats"):
                        for tag in dearpygui.get_item_children("table_stats")[1]:
                            dearpygui.delete_item(tag)

                    with dearpygui.table_row():
                        dearpygui.add_text(mh)
                        dearpygui.add_text(cf)
                        dearpygui.add_text(cb)
                except NoSuchWindowException as e:
                    print(f"error scraping stats [{type(e).__name__}]:\n{e} | {label} | {value}\n")
                    sys.exit(0)

                # Calculate days, hours, minutes, and seconds
                elapsed_time = time.time() - start_time
                days, remainder = divmod(elapsed_time, 86400)
                hours, remainder = divmod(remainder, 3600)
                minutes, seconds = divmod(remainder, 60)

                dearpygui.set_value("label_updates", f"Elapsed Time: {int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s")
                time.sleep(1)

class Conditions:
    """callback conditions that determine how the Callbacks.submit function will run"""
    LOGGING_IN         : bool = False
    LOGGING_IN_TIME    : int  = None
    AWAITING_AUTH      : bool = False

class Callbacks:
    @staticmethod
    def submit() -> str | None:
        """submit button functionality"""
        textbox_value = str(dearpygui.get_value("textbox_email"))

        if Conditions.AWAITING_AUTH:
            if len(textbox_value) != 4 or not textbox_value.isdigit():
                print("invalid auth code, check it and try again")
                return
            WebScraper.verify_email(textbox_value)
        else:

            if Conditions.LOGGING_IN and time.time() - Conditions.LOGGING_IN_TIME < 15:
                remaining_time = 15 - (time.time() - Conditions.LOGGING_IN_TIME)
                print(f"You must wait {remaining_time:.0f} seconds before you can send another email")
                return

            if not any(s in textbox_value for s in ["@", ".com"]) or textbox_value.strip() == "":
                print("invalid email")
                return

            Conditions.LOGGING_IN = True
            Conditions.LOGGING_IN_TIME = time.time()

            WebScraper.load_login_page(textbox_value)

if __name__ == "__main__":
    print("hello world")
