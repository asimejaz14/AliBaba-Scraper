import re
import time
import sys
from bs4 import BeautifulSoup
from pyfiglet import Figlet
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, InvalidArgumentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from nltk import word_tokenize
from nltk.corpus import stopwords
from security import safe_requests

f = Figlet(font='slant')
print(f.renderText('Alibaba Bot'))

chrome_options = webdriver.ChromeOptions();
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--incognito")
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)"
                            " Chrome/47.0.2526.111 Safari/537.36")


def detect_lang(text):
    lang_ratios = {}

    tokens = word_tokenize(text)
    words = [word.lower() for word in tokens]

    for language in stopwords.fileids():
        stopwords_set = set(stopwords.words(language))
        words_set = set(words)
        common_elements = words_set.intersection(stopwords_set)

        lang_ratios[language] = len(common_elements)
    return max(lang_ratios, key=lang_ratios.get)


def get_supplier_urls(url_get, driver):

    try:
        driver.get(url_get)
        time.sleep(5)
        driver.refresh()
        # /html/body/div[1]/div[2]/div/div[1]/div/div[2]
        select_option = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located(
                (By.XPATH, '//html/body/div[1]/div[2]/div/div[1]/div/div[2]')))
        #                   /html/body/div[1]/div[2]/div/div[1]/div/div[2]
        html = select_option.get_attribute('innerHTML')

        soup = BeautifulSoup(html, 'lxml')
        supplier_contact_urls = []
        for item in soup.findAll("a", {"class": "cd"}, href=True):
            supplier_contact_urls.append(item['href'])

        return supplier_contact_urls
    except InvalidArgumentException:
        pass


def login(username, password, driver):
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

    # login
    try:
        select_option = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, '//html/body/div[2]/div[2]/div[2]/div[1]/div/form/div[5]/input[2]')))
        select_option.click()
    except TimeoutException:
        pass


def extract_website(url):
    print("Sending request to:", url)
    res = safe_requests.get(url)
    soup = BeautifulSoup(res.content, 'lxml')
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

    urls_of_company = []
    for item in soup.findAll("td", {"class": "item-value"}):
        if re.match(regex, item.text):
            da = str(item.parent.contents)
            d = re.findall(regex, da)
            for i in d:
                if i:
                    # print(i[0])
                    urls_of_company.append(i[0])

    return urls_of_company


def get_emails():
    with open('credentials.txt', encoding='utf-8') as file:
        creds = file.readlines()
        with open('emails.txt', 'w', encoding='utf-8') as file:
            for cred in creds:
                driver = webdriver.Chrome(options=chrome_options)
                cred.rstrip('\n')
                cr = cred.split(':')
                username = cr[0]
                password = cr[1]
                print("Logging in", username, password)
                login(username, password, driver)
                time.sleep(5)
                driver.get('https://profile.alibaba.com/receive_list.htm')
                # get page numbers
                soup = BeautifulSoup(driver.page_source, 'lxml')
                d = soup.find("div", {"class": "ui2-pagination ui2-pagination-top"})
                for i in d.find_all('a'):
                    i.decompose()
                for i in d.find_all('span'):
                    i.decompose()
                page_number = d.text.strip()
                num = int(page_number.split('/')[1].strip())

                # grabbing emails

                for i in range(0, num):
                    soup = BeautifulSoup(driver.page_source, 'lxml')
                    for item in soup.findAll("div", {"class": "email"}, title=True):
                        print(item['title'])
                        file.write(item['title'])
                        file.write('\n')
                    try:
                        time.sleep(5)
                        select_option = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located(
                                (By.CLASS_NAME, 'next')))
                        select_option.click()
                    except TimeoutException:
                        pass
                driver.quit()


def request_cards():
    with open('credentials.txt', encoding='utf-8') as file:
        creds = file.readlines()

        for cred in creds:
            driver = webdriver.Chrome(options=chrome_options)
            cred.rstrip('\n')
            cr = cred.split(':')
            username = cr[0]
            password = cr[1]
            print("Logging in", username, password)
            login(username, password, driver)
            time.sleep(5)
            driver.get('https://profile.alibaba.com/sent_list.htm')
            # get page numbers
            soup = BeautifulSoup(driver.page_source, 'lxml')
            d = soup.find("div", {"class": "ui2-pagination ui2-pagination-top"})
            for i in d.find_all('a'):
                i.decompose()
            for i in d.find_all('span'):
                i.decompose()
            page_number = d.text.strip()
            num = int(page_number.split('/')[1].strip())
            lan = soup.find("div", {"class": "title"})
            if detect_lang(lan.text) == 'english':

                for i in range(0, num):
                    n = 1
                    for ii in range(0, 10):
                        try:
                            req_button = WebDriverWait(driver, 3).until(
                                EC.presence_of_element_located(
                                    (By.XPATH,
                                     f'//html/body/div[1]/div/div[1]/div/div/div/div[2]/div/div/div[2]/div[2]/ul/li[{n}]/div[5]/ul/li[1]/a')))
                            time.sleep(3)
                            req_button.click()
                            n += 1
                        except NoSuchElementException:
                            n += 1
                        except StaleElementReferenceException:
                            time.sleep(3)
                            ii -= 1
                        except TimeoutException:
                            n += 1


                    try:
                        time.sleep(5)
                        select_option = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located(
                                (By.CLASS_NAME, 'next')))
                        select_option.click()
                    except TimeoutException:
                        pass

            else:
                for i in range(0, num):
                    n = 1
                    for ii in range(0, 10):
                        try:
                            req_button = WebDriverWait(driver, 3).until(
                                EC.presence_of_element_located(
                                    (By.XPATH, f'//html/body/div[1]/div/div[1]/div/div/div/div[2]/div/div/div[2]/div[2]/ul/li[{n}]/div[5]/ul/li[1]/a')))
                            time.sleep(3)
                            req_button.click()

                            n += 1
                        except NoSuchElementException:
                            n += 1
                        except StaleElementReferenceException:
                            time.sleep(3)
                            ii -= 1
                        except TimeoutException:
                            n += 1

                    try:
                        time.sleep(5)
                        select_option = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located(
                                (By.CLASS_NAME, 'next')))
                        select_option.click()
                    except TimeoutException:
                        pass

            driver.quit()


def main():
    while True:
        print('1- Extract supplier websites')
        print('2- Grab Emails')
        print('3- Request Card')
        print('4- Exit')
        print()
        choice = int(input("Choose: "))
        print()
        count = 0
        if choice == 1:
            try:
                driver = webdriver.Chrome(options=chrome_options)
                file_path = input("Input URL file: ")
                file_path = file_path.strip('\"')
                file_path = file_path.rstrip('\"')
            except FileNotFoundError:
                print("File not found")
                exit()

            with open(file_path, encoding='utf-8') as file:
                urls = file.readlines()
            with open("Supplier Websites.txt", 'w', encoding='utf-8') as file:

                for url in urls:
                    url = url.rstrip('\n')
                    if url:
                        contact_info_urls = get_supplier_urls(url, driver)
                        if contact_info_urls:
                            for info_url in contact_info_urls:
                                count += 1
                                if count == 10:
                                    time.sleep(5)
                                    count = 0
                                website = extract_website(info_url)
                                for w in website:
                                    if w is not None:
                                        print("Response URL(s):", w)

                                        file.write(w)
                                        file.write('\n')
                                print()
            driver.quit()

        elif choice == 2:
            get_emails()

        elif choice == 3:
            request_cards()

        elif choice == 4:
            driver.quit()
            sys.exit()


if __name__ == '__main__':
    main()

# verifying login
# select_option = WebDriverWait(driver, 60).until(
#     EC.presence_of_element_located((By.XPATH, '//html/body/div[1]/header/div[2]/div[3]/div/div/form/div[2]')))


# --add-data "venv\Lib\site-packages\pyfiglet;./pyfiglet"
