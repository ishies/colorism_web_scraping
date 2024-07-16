import decimal
import time
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def scroll_and_load(driver):
    scroll_increment = 1000  # Scroll down by 1000 pixels each time
    scroll_pause_time = 2  # Time to pause after each scroll

    last_height = driver.execute_script("return document.body.scrollHeight")
    new_height = last_height
    max_attempts = 20  # Number of scroll attempts
    attempts = 0

    while attempts < max_attempts:
        driver.execute_script(f"window.scrollTo(0, {last_height + scroll_increment});")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            attempts += 1
        else:
            attempts = 0

        last_height = new_height

def get_all_page_content(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    # Perform initial scroll and load
    scroll_and_load(driver)

    # Ensure all elements are loaded
    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'col-6.col-sm-6.col-md-3'))
    )

    page_content = driver.page_source
    driver.quit()
    return page_content

def scrape_fabindia_products(url):
    page_content = get_all_page_content(url)
    soup = BeautifulSoup(page_content, 'html.parser')

    products = []
    product_elements = soup.find_all('div', class_='col-6 col-sm-6 col-md-3')
    print(f"Found {len(product_elements)} product elements")

    for i, product in enumerate(product_elements):
        product_info = {}

        image_element = product.find('img')
        product_info['image'] = image_element['src'] if image_element else None

        name_element = product.find('a', class_='link d-lg-none')
        product_info['name'] = name_element.text.strip() if name_element else None

        price_element = product.find('span', class_='sales')
        price_str = price_element.text.strip() if price_element else None

        if price_str:
            cleaned_price_str = price_str.replace('$', '').replace(',', '').strip()
            decimal_price = decimal.Decimal(cleaned_price_str)
            product_info['price'] = float(decimal_price)
        else:
            product_info['price'] = None

        product_info['index'] = i + 72
        products.append(product_info)

        print(product_info)  # Debugging line

    return products

def save_to_json(products, filename='biba_products.json'):
    try:
        # Load existing data from the JSON file
        with open(filename, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = []

    # Append new products to the existing data
    existing_data.extend(products)

    # Write back to the JSON file
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)

# URL to scrape
url = 'https://www.biba.in/intl/kurtas-and-tops/shrugs-and-jackets/'

# Scrape the products
products = scrape_fabindia_products(url)
save_to_json(products, filename='biba_products.json')

for product in products:
    print(product)