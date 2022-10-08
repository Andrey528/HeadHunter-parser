from bs4 import BeautifulSoup
import json
import tqdm
import time
from requests_tor import RequestsTor

data = { #словарь для спарсенных данных
    "data":[]
}

proxies = { #прокси, по умолчанию тор браузер имеет контрольный порт 9150. Меняется в файле Tor Browser\Browser\TorBrowser\Data\Tor\torrc
    'http': 'socks5h://localhost:9150',
    'https': 'socks5h://localhost:9150'
}

req = RequestsTor()

for page in range(0, 40): #поиск по ключевому словосочетанию "python разработчик" выдал 40 страниц результата. Страницы индексируются с 0.
    url = f"https://novosibirsk.hh.ru/search/vacancy?text=python+разработчик&from=suggest_post&salary=&clusters=true&area=113&no_magic=true&ored_clusters=true&enable_snippets=true&page={page}&hhtmFrom=vacancy_search_list"

    resp = req.get(url, proxies=proxies, headers={'user-agent': 'Mozilla/5.0'}) #задаем используемый в сообщении браузер для бота, передаем заданные прокси.
    print(resp) #код 200 говорит об удачном переходе бота на сайт. 403 говорит о блокировке бота сайтом.

    soup = BeautifulSoup(resp.text, "lxml") #используем библиотеку lxml.
    tags = soup.find_all(attrs={"data-qa":  "serp-item__title"}) #тег ссылок на название вакансий и их описание.
    tag_region = soup.find_all("div", attrs={"data-qa": "vacancy-serp__vacancy-address"}) #регион вакансии пишется на главной странице под титулом объявления.

    counter = 0; #счетчик для извлечения элементов списка tag_region.

    for iter in tqdm.tqdm(tags):
        time.sleep(2) #задержка для имитации действий человека.

        resp_object = req.get(iter.attrs["href"], proxies=proxies, headers={'user-agent': 'Mozilla/5.0'}) #переходим по ссылке объявления и парсим информацию оттуда.
        soup_object = BeautifulSoup(resp_object.text, "lxml")

        tag_exp = soup_object.find(attrs={"data-qa": "vacancy-experience"}) #ищем на странице вакансии информацию об требуемом опыте.
        if tag_exp is None: #обработка none значений для требуемого опыта.
            experience = "Не указан"
        else:
            experience = tag_exp.text

        tag_price = soup_object.find(attrs={"data-qa": "vacancy-salary-compensation-type-net"}) #поиск предлагаемой для вакансии зарплаты.
        if tag_price is None: #обработка none значений для зарплаты.
            salary = "Не указана"
        else:
            salary = tag_price.text

        data["data"].append({"Title": iter.text, "Experience": experience, "Salary": salary, "Region": tag_region[counter].text}) #добавление в словарь данных о титуле вакансии, требуемый опыт, предлагаемая зарплата, регион.
        counter += 1 #инкремент счетчика для извлечения значений региона

with open("data.json", "w") as file: #запись в json файл.
    json.dump(data, file, ensure_ascii=False) #при таких настройках будет читатся русская кодировка.