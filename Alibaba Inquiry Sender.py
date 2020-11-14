import ctypes
import time

from bs4 import BeautifulSoup
from pyfiglet import Figlet
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

f = Figlet(font='slant')
print(f.renderText('Alibaba Inquiry Sender'))

chrome_options = webdriver.ChromeOptions();
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--incognito")
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)"
                            " Chrome/47.0.2526.111 Safari/537.36")


def countdown(t):
    while t > 0:
        # print("Moving to next supplier page in", t, " seconds")
        t -= 1
        time.sleep(1)


def get_supplier_urls(url_get):
    driver.get(url_get)
    # /html/body/div[1]/div[2]/div/div[1]/div/div[2]
    select_option = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located(
            (By.XPATH, '//html/body/div[1]/div[2]/div/div[1]/div/div[2]')))
    #                   /html/body/div[1]/div[2]/div/div[1]/div/div[2]
    html = select_option.get_attribute('innerHTML')

    soup = BeautifulSoup(html, 'lxml')
    supplier_urls = []
    for item in soup.findAll("div", {"data-spm": "35"}):
        # button csp
        contact = item.find("a", {"class": "button csp"}, href=True)
        contact_url = 'https:' + contact['href']
        supplier_urls.append(contact_url)

    return supplier_urls


try:
    file_path = input("Input URL file: ")
    file_path = file_path.strip('\"')
    file_path = file_path.rstrip('\"')
except FileNotFoundError:
    print("File not found")
    exit()

msg = ''
with open('message.txt', encoding='utf-8') as file:
    msg = file.read()

urls_to_capture = []
with open(file_path, encoding='utf-8') as file:
    urls = file.readlines()

    for url in urls:
        url = url.rstrip('\n')
        urls_to_capture.append(url)

with open('credentials.txt', encoding='utf-8') as file:
    creds = file.readlines()


def login(username, password):
    driver.get('https://passport.alibaba.com/icbu_login.htm')

    # username
    select_option = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located(
            (By.XPATH, '//html/body/div[2]/div[2]/div[2]/div[1]/div/form/div[4]/dl[1]/dd/div/input')))
    select_option.click()
    select_option.send_keys(username)

    # password
    select_option = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located(
            (By.XPATH, '//html/body/div[2]/div[2]/div[2]/div[1]/div/form/div[4]/dl[2]/dd/div/input')))
    select_option.click()
    select_option.send_keys(password)
    try:
        select_option = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, '//html/body/div[2]/div[2]/div[2]/div[1]/div/form/div[4]/dl[3]/dd[1]/div/div/div[1]/div[2]/span')))
        ctypes.windll.user32.MessageBoxW(0, "Press ok and verify", "Login", 1)
        time.sleep(15)
        select_option = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located(
                (By.XPATH, '//html/body/div[2]/div[2]/div[2]/div[1]/div/form/div[5]/input[2]')))
        select_option.click()
    except TimeoutException:

    # time.sleep(15)

        # login
        select_option = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, '//html/body/div[2]/div[2]/div[2]/div[1]/div/form/div[5]/input[2]')))
        select_option.click()


# verifying login
# select_option = WebDriverWait(driver, 60).until(
#     EC.presence_of_element_located((By.XPATH, '//html/body/div[1]/header/div[2]/div[3]/div/div/form/div[2]')))

errors = []

with open('errors.txt', 'w', encoding='utf-8') as file:
    counter1 = 0
    for url in urls_to_capture:

        # spliting username and password

        if counter1 == len(creds):
            counter1 = 0
        cr_splited = creds[counter1].split(':')
        counter1 += 1
        username = cr_splited[0]
        password = cr_splited[1]
        password = password.rstrip('\n')
        print("Logging in", username, password)
        driver = webdriver.Chrome(options=chrome_options)
        login(username, password)
        time.sleep(5)
        sup_urls = get_supplier_urls(url)
        print(f"Sending inquiry to {len(sup_urls)} suppliers one by one")

        counter = 0
        for s_url in sup_urls:
            counter += 1
            try:
                # if counter ==3:
                #     break
                time.sleep(3)
                driver.get(s_url)
                select_option = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//html/body/div[2]/div/form/div[1]/div[4]/div/textarea')))
                select_option.click()

                select_option.send_keys(msg)
                # /html/body/div[2]/div/div[2]/div/span

                select_option = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//html/body/div[2]/div/form/div[1]/div[5]/div[3]/div[2]/input')))
                select_option.click()

                # print("URL:", counter)
                # print(s_url)
                print('Inquiry sent')
            except TimeoutException:
                print("INVALID", s_url)
                errors.append(s_url)
            except NoSuchElementException:
                print("INVALID", s_url)
                errors.append(s_url)
            except ElementClickInterceptedException:
                select_option = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//html/body/div[2]/div/div[2]/div/span')))
                select_option.click()
                select_option = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//html/body/div[2]/div/form/div[1]/div[4]/div/textarea')))
                select_option.click()

                select_option.send_keys(msg)
                # /html/body/div[2]/div/div[2]/div/span

                select_option = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//html/body/div[2]/div/form/div[1]/div[5]/div[3]/div[2]/input')))
                select_option.click()

                # print("URL:", counter)
                # print(s_url)
                print('Inquiry sent')

            final_errors = set(errors)
            for f in final_errors:
                file.write(f)
                file.write('\n')
        driver.quit()
        print()
        print("Automated bot delay 25 mins")
        print()

        countdown(1500)
        # login()

print("Press any key to exit...")
driver.quit()

# --add-data "venv\Lib\site-packages\pyfiglet;./pyfiglet"