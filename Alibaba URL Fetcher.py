from bs4 import BeautifulSoup
from pyfiglet import Figlet
from selenium import webdriver

f = Figlet(font='slant')
print(f.renderText('Alibaba URL Fetcher'))

chrome_options = webdriver.ChromeOptions();
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--incognito")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)"
                            " Chrome/47.0.2526.111 Safari/537.36")



urls = []
try:
    file_path = input("Input URL file: ")
    file_path = file_path.strip('\"')
    file_path = file_path.rstrip('\"')
except FileNotFoundError:
    print("File not found")
    exit()
with open(file_path) as file:
    urls = file.readlines()

driver = webdriver.Chrome(options=chrome_options)

urls_to_save = []
with open('URLs.txt', 'w', encoding='utf-8') as file:
    counter = 0
    for i in urls:
        i = i.rstrip('\n')
        driver.get(i)
        while True:
            try:
                counter += 1
                print(counter)
                # if counter == 6:
                #     driver.quit()
                #     exit()

                html = ''
                soup = BeautifulSoup(driver.page_source, 'lxml')
                n = soup.find("a", {"class": "next"}, href=True)
                url = 'https://' + n['href'].lstrip('//')
                print(driver.current_url)
                file.write(driver.current_url)
                file.write('\n')
                driver.get(url)
            except TypeError:
                break

driver.quit()
