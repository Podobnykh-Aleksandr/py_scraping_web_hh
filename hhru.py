import json
from selenium import webdriver
from bs4 import BeautifulSoup as BS
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService


class ParserVacancy:
    search = None
    driver = None
    quantity_pages = None
    chrome_options = Options()
    service = None
    list_url = []
    dict_final = {}

    def __init__(self, search, quantity_pages):
        self.search = search
        self.quantity_pages = quantity_pages
        self.chrome_options.add_argument('--disable-extensions')
        self.chrome_options.add_argument('--disable-plugins')
        self.chrome_options.add_argument('--headless=new')
        self.service = ChromeService(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)

    def get_all_url(self):
        for page in range(self.quantity_pages):
            url = f'https://spb.hh.ru/search/vacancy?text={self.search}&area=1&area=2&search_field=description&page={page}'
            self.list_url.append(url)

    def get_vacancy_info(self):
        for url in self.list_url:
            self.driver.get(url)
            soup_main = BS(self.driver.page_source, 'html.parser')
            all_tags = soup_main.find_all(class_='serp-item')

            for tag in all_tags:
                title = tag.find(class_='serp-item__title')
                if title.text.count('Django') or title.text.count('Flask'):
                    href = tag.find(class_='serp-item__title').get('href')
                    salary = tag.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
                    salary = 'Договорная' if salary is None else salary.text.replace('\u202f', '')
                    name_company = tag.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'}).text.split()
                    name_company = ' '.join(name_company)
                    city = tag.find('div', attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text.split(',')[0]

                    self.dict_final.setdefault(href)
                    self.dict_final[href] = {'salary': salary}
                    self.dict_final[href].update({'name_company': name_company})
                    self.dict_final[href].update({'city': city})

    def write_json(self):
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(self.dict_final, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    parser = ParserVacancy('python', 10)
    parser.get_all_url()
    parser.get_vacancy_info()
    parser.driver.quit()
    parser.write_json()
