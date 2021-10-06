import datetime
import os
import random
import time
import requests
import urllib3
from bs4 import BeautifulSoup
import openpyxl
from selenium import webdriver
from urllib3.exceptions import InsecureRequestWarning
from PIL import Image
from selenium.webdriver.common.keys import Keys


user_agents_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
    ]

headers = {
    "User-Agent": random.choice(user_agents_list)
}

BASE_LINK_DEPOSIT_PHOTOS = 'https://ru.depositphotos.com/stock-photos'
BASE_LINK_SHUTTER_STOCK = 'https://www.shutterstock.com/ru'


def converter_deposit_to_soup(search_rubric, offset: int):
    soup_list = []
    url = f"{BASE_LINK_DEPOSIT_PHOTOS}/{search_rubric.replace(' ', '-')}.html"
    for count in range(1, offset + 1):
        get_page = requests.get(url, headers=headers)
        time.sleep(2)
        if get_page.status_code != 200:
            print(f"status code isn't 200. STATUS_CODE is {get_page.status_code}")
        html = BeautifulSoup(get_page.content, "html.parser")
        soup_list.append(html)
        counter = count * 100
        url = f"{BASE_LINK_DEPOSIT_PHOTOS}/{search_rubric.replace(' ', '-')}.html?offset={counter}"
    return soup_list


def ready_links(soup_list: list):
    ready_data = []
    for soup in soup_list:
        get_photo_link = soup.select(
            "a > picture > img"
        )
        if get_photo_link:
            for link in get_photo_link:
                try:
                    ready_data.append(link['src'])
                except KeyError as e:
                    ready_data.append(link['data-src'])
        else:
            print("По вашему запросу картинок не найдено!")
            input('Нажмите Enter')
            return
    print(f"Спарсены {len(ready_data)} кол-во картинок с первого сайта! переходим к сохранению!")
    return ready_data


def download_photos(link_list: list):
    photo_info = []
    for link in link_list:
        try:
            photo_name = link.split('/')[-1]
            photo_format = photo_name.split(".")[-1]
            file_path = './site_deposit_photos'
            if not os.path.exists(file_path):
                os.mkdir('./site_deposit_photos')
            urllib3.disable_warnings(InsecureRequestWarning)
            save_data = requests.get(link, verify=False, headers=headers)
            with open(f"{file_path}/{photo_name}", 'wb') as file:
                file.write(save_data.content)
            with Image.open(f"{file_path}/{photo_name}") as img:
                width, height = img.size
            sizes_data = {
                "file_name": photo_name,
                "width": width,
                "height": height,
                'file_format': photo_format
            }
            photo_info.append(sizes_data)
        except Exception as e:
            print('Что то пошло не так.. пропустил этот файл и перешёл на следующий!')
            continue
    return photo_info


def save_photo_info(info_list: list, file_name, file_path):
    book = openpyxl.Workbook()
    sheet = book.active
    sheet['A1'] = 'Название фото'
    sheet['B1'] = 'Ширина фото(px)'
    sheet['C1'] = 'Высота фото(px)'
    sheet['D1'] = 'Формат фото'

    row = 2

    for info in info_list:
        sheet[row][0].value = info['file_name']
        sheet[row][1].value = info['width']
        sheet[row][2].value = info['height']
        sheet[row][3].value = info['file_format']
        row += 1

    if not os.path.exists(file_path):
        os.mkdir(file_path)
    book.save(f"{file_path}{file_name.replace(' ', '-')}-{datetime.date.today()}.xlsx")
    book.close()
    print("Информация сохранена успешно!")
    return True


def parse_with_selenium(link):
    options = webdriver.FirefoxOptions()
    options.set_preference('general.useragent.override', random.choice(user_agents_list))
    options.set_preference("dom.webdriver.enabled", False)
    options.headless = True
    driver = webdriver.Firefox(
        executable_path='geckodriver.exe',
        options=options
    )
    try:
        driver.get(url=link)
        time.sleep(5)
        html_page = driver.find_element_by_tag_name("html")
        for i in range(150):
            html_page.send_keys(Keys.DOWN)
        time.sleep(10)
        with open("file.html", 'w', encoding='utf-8') as file:
            file.write(driver.page_source) 
        with open("file.html", 'r', encoding='utf-8') as f:
            parser_file = f.read()
        soup = BeautifulSoup(parser_file, 'html.parser')
        get_link = soup.select("div.z_h_b900b > a.z_h_81637 > img")
        if get_link:
            try:
                for links_ in get_link:
                    link = links_['src']
                    link_data.append(link)
            except KeyError:
                print('')
    finally:
        driver.close()
        driver.quit()
        if not link_data:
            return False
        print(f"Спарсены {len(link_data)} кол-во картинок с второго сайта! переходим к сохранению!")
        return link_data


def save_shutter(link_list: list):
    photo_info = []
    for link in link_list:
        try:
            photo_name = link.split('/')[-1]
            photo_format = photo_name.split(".")[-1]
            file_path = './site_shutter_photos'
            if not os.path.exists(file_path):
                os.mkdir('./site_shutter_photos')
            urllib3.disable_warnings(InsecureRequestWarning)
            save_data = requests.get(link, verify=False, headers=headers)
            with open(f"{file_path}/{photo_name}", 'wb') as file:
                file.write(save_data.content)
            with Image.open(f"{file_path}/{photo_name}") as img:
                width, height = img.size
            sizes_data = {
                "file_name": photo_name,
                "width": width,
                "height": height,
                'file_format': photo_format
            }
            photo_info.append(sizes_data)
        except Exception as e:
            print('Что то пошло не так.. пропустил этот файл и перешёл на следующий!')

    return photo_info


if __name__ == "__main__":
    get_rubric = input("Что ищем? Ввод: ")
    try:
        get_offset = int(input("Сколько страниц хотим парсить? Ввод: "))
    except ValueError:
        get_offset = int(input("Сколько страниц хотим парсить? Ввод: "))
    get_file_name = input('Вводите название файла ексель(без .xlsx): ')
    parse_deposit = converter_deposit_to_soup(get_rubric, get_offset)
    if parse_deposit:
        links_ready = ready_links(parse_deposit)
        if links_ready:
            download_and_get_info = download_photos(links_ready)
            save_photo_info(download_and_get_info, get_file_name, './site_deposit_photos/photo_info/')
    get_url = f"{BASE_LINK_SHUTTER_STOCK}/search/{get_rubric.replace(' ', '+')}"
    link_data = []
    for get in range(1, get_offset + 1):
        links = parse_with_selenium(get_url)
        get_url = f"{BASE_LINK_SHUTTER_STOCK}/search/{get_rubric.replace(' ', '+')}?page={get + 1}"
    if link_data:
        shutter = save_shutter(link_data)
        save_photo_info(shutter, get_file_name, './site_shutter_photos/photo_info/')