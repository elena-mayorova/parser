# ===============================================================================================================================================================
# Необходимы библиотеки: beautifulsoup4, selenium, time
# Установить: pip install beautifulsoup4 mysql-connector-python
# Если используете Firefox (или другой браузер на движке Gecko), 
# то для работы с Selenium необходимо установить прокси geckodriver - https://github.com/mozilla/geckodriver/releases
# ===============================================================================================================================================================

from bs4 import BeautifulSoup
"""
BeautifulSoup4 - это библиотека, значительно облегчающая процесс парсинга HTML и XML файлов.
"""

from selenium import webdriver
"""
Selenium WebDriver – это программная библиотека для управления браузерами.
"""

import time
"""
Time - модуль для работы со временем в Python.
"""

import mysql.connector
"""
MySQL Connector/Python - это драйвер, который позволяет взаимодействовать с серверами MySQL прямо из кода.
"""


# Переменная, содержащая адрес страницы, которую мы хотим парсить.
URL = "https://www.ozon.ru/category/plastikovyy-konstruktor-31443/?brand=19159896%2C166857815%2C87345827"

# Переменная, содержащая количество секунд, на которое мы будем приостанавливать программу, чтобы не быть заблокированными сайтом.
scroll_pause_time = 9

# Объект класса Webdriver для браузера Firefox с явным указанем каталога, в котором лежит geckodriver, загруженный ранее.
driver = webdriver.Firefox(executable_path='C:\\geckodriver-v0.30.0-win64\\geckodriver.exe')

# Список (почти как массив, но может одновременно содеражать объекты разных типов),
# в котором будет лежать HTML-структура сайта.
products = []

# В цикле проходим по интересующему нас количеству страниц.
for page_num in range (1,3):

    # Добавляем в URL-адрес номер страницы.
    # В дальнейшем работаем с этой конкретной страницей.
    URL = f"{URL}&page={page_num}"
    
    # Передаем веб-драйверу адрес, чтобы он могу установить соединение.
    driver.get(URL)

    # Определяем высоту открытой веб-драйвером страницы.
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Прокручиваем вниз
        # window.scrollTo(x-координата, y-координата)
        # x-координата - пиксель оси x, который будет располагаться в левом верхнем углу
        # y-координата - пиксель оси y, который буде располагаться слева сверху
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Ждем прогрузки страницы, одновременно избегая блокировки браузером.
        time.sleep(scroll_pause_time)

        # Вычисляем новую высоту и сравниваем ее с предыдущей.
        new_height = driver.execute_script("return document.body.scrollHeight")
        # Если новая равна предыдущей (то есть мы дошли до конца страницы), прерываем цикл
        if new_height == last_height:
            break
        last_height = new_height

    # Объект класса BeautifulSoup, который содержит в себе страницу в виде вложенной структуры данных
    # Именно из этого объекта мы и будем доставать интересующую нас информацию.
    # page_source - это метод веб-драйвера, возвращающий исходный код страницы
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Добавляем в массив все элементы <div> класса "bi1"
    # Метод find_all() просматривает потомков тега и извлекает всех потомков, которые соответствую вашим фильтрам.
    # Больше про find_all() - https://www.crummy.com/software/BeautifulSoup/bs4/doc.ru/bs4ru.html#find-all
    products.extend(soup.find_all("div", {"class": "bi1"}))

    # Возвращаем исходный адрес строки
    URL = "https://www.ozon.ru/category/plastikovyy-konstruktor-31443/?brand=19159896%2C166857815%2C87345827"

# Закрываем веб-браузер, он нам больше не нужен.
driver.close()

# Открываем связь с нашим сервером MySQL с помощью объекта класса mysql.connector
# и метода connect
cnx = mysql.connector.connect(user='root', password='12345',
                              host='localhost',
                              database='my_parser')
# Курсор - это структура, посредством которой мы общаемся с БД. Они принимает от нас запрос с данными,
# передает результаты в базу (если это запросы типа INSERT) или возвращает его результаты нам (если это запросы типа SELECT).
cursor = cnx.cursor()

for product in products:
    
    # Метод find_all() сканирует весь документ в поиске всех результатов, но иногда вам нужен только один.
    # Если вы знаете, что в документе есть только один тег <body>, нет смысла сканировать весь документ в поиске остальных.
    # Если find() не может ничего найти, он возвращает None
    # 
    # Метод findChildren() находит все дочерние элементы тега. В данном случае мы ищем дочерние теги <span> предыдущего найденного элемента,
    # но при этом выбираем из них нулевой элемент.
    # 
    # get_text() возвращает весь текст документа или тега в виде единственной строки Unicode.
    # Используем его, когда нам нужна только текстовая часть документа или тега.
    product_name = product.find("span", {"class": "a7y a8a2 a8a6 a8b2 f-tsBodyL bj5"}).findChildren("span")[0].get_text()

    # после этого мы аналогичным образом находим продавца
    # единственное отличие заключается в том, что у товара он может быть не указан
    # в этом случае продавцом является Ozon Express
    # для отбора таких случаев мы прописываем условие
    # если метод find возвращает None, то есть мы не находим продавца,
    # то мы вручную указываем продавца как Ozon Express
    product_seller = product.find("div", {"class": "b0d5 b0d8"})
    if product_seller is not None:
        # findChild() возвращает единственный дочерний элемент тега. Используем, когда знаем, что 
        # у выбранного тега есть только
        # один дочерний элемент.
        product_seller = product.find("div", {"class": "b0d5 b0d8"}).findChildren("span")[3].findChildren("font")[1].findChild().get_text()
    else:
        product_seller = 'Ozon Express'

    # теперь найдем цену
    # здесь может быть два варианта, цена без скидки и цена со скидкой
    # но их мы находим по сути абсолютно так же, как до этого продавца и название
    
    product_price = product.find("span", {"class": "ui-p2 ui-o9"})
    if product_price is not None:
        # если мы находим вот такую цену без скидки, то ее и указываем
        product_price = product.find("span", {"class": "ui-p2 ui-o9"}).get_text()
    else:
        # если мы ее не находим, то выбираем элемент с классом вот такой цены
        product_price = product.find("span", {"class": "ui-o6 ui-o9"}).get_text()

    product_price_sale = product.find("span", {"class": "ui-o6 ui-o9 ui-p1"})
    if product_price_sale is not None:
        product_price_sale = product.find("span", {"class": "ui-o6 ui-o9 ui-p1"}).get_text()
    else:
        product_price_sale = 'Нет скидки'

    # Строка с результатами поиска.
    result = f"Название: {product_name}\n\
    Продавец: {product_seller}\n\
    Цена: {product_price}\n\
    Цена со скидкой: {product_price_sale}\n"


    print(result)

    # Кортеж с данными о продукте, которые мы только что нашли.
    # Отличие кортежа от списка в том, что он защищен от изменений и занимает меньше места..
    data_product = (product_name, product_seller, product_price, product_price_sale)

    # Строка с запросом в базу на внесение новых данных.
    # Символы %s здесь используют вместо данных, которые мы хотим вставить.
    # В дальнейшем сам курсор приведет наши данные (product_name, product_seller...) из
    # типа данных Python в тип данных, который понимает MySQL. То есть каждый %s
    # будет заменен на соответствующую переменную из кортежа data_product (в том же порядке,
    # в котором они расположены в кортеже).
    add_product = ("INSERT INTO parser "
               "(name, seller, price, price_sale) "
               "VALUES (%s, %s, %s, %s)")
    

    # Выполняем запрос с помощью метода execute().
    # Передаем в него сначала запрос, а потом данные, которые в него нужно внести.
    cursor.execute(add_product, data_product)

# В конце обязательно коммитим изменения БД.
cnx.commit()
# Удаляем курсор и закрываем связь с БД.
cursor.close()
cnx.close()