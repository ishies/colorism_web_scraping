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

def scroll_to_bottom(driver):
    # Scroll to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Adjust sleep time as needed for content to load

def get_all_page_content(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    # Scroll down several times to load all products
    for _ in range(10):  # Adjust the number of scrolls as needed
        scroll_to_bottom(driver)

    # Wait briefly for content to load after scrolling
    time.sleep(5)  # Adjust sleep time as needed

    # Get the page source after all content is loaded
    page_content = driver.page_source

    driver.quit()
    return page_content

def scrape_fabindia_products(url):
    page_content = get_all_page_content(url)
    soup = BeautifulSoup(page_content, 'html.parser')

    products = []

    # Find all elements
    product_elements = soup.find_all('div', class_='product col-sm-4 col-12')
    i = 0
    for product in product_elements:

        product_info = {}

        # Extract Image
        # image_element = product.find('app-fab-product-grid-item')
        # if image_element:
        #     link_element = image_element.find('a')
        #     if link_element:
        #         cx_media_element = link_element.find('cx-media')
        #         if cx_media_element:
        #             img_element = cx_media_element.find('img')
        #             if img_element:
        #                 product_info['image'] = img_element.get('src', '')
        #             else:
        #                 product_info['image'] = 'No src'
        #         else:
        #             product_info['image'] = 'No cx-media'
        #     else:
        #         product_info['image'] = "No a"
        # else:
        #     product_info['image'] = 'No app-fab-product-grid-item'

        image_element = product.find('img')
        product_info['image'] = image_element.get('src', '') if image_element else None

        # Extract Other Info
        name_element = product.select_one('p.product-description.my-0') 
        product_info['name'] = name_element.text.strip() if name_element else None   

        price_element = product.find('span', class_='offer-amount')
        price_str = price_element.text.strip() if price_element else None
        cleaned_price_str = price_str.replace('$', '').replace(',', '').strip()
        decimal_price = decimal.Decimal(cleaned_price_str)
        product_info['price'] = float(decimal_price)

        product_info['index'] = i
        i += 1

        products.append(product_info)
    
    return products

def save_to_json(products, filename='fabindia_kids_products.json'):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(products, file, ensure_ascii=False, indent=4)

# URL to scrape
url = 'https://www.fabindia.com/shop/kids-products'


# Scrape the products
products = scrape_fabindia_products(url)
save_to_json(products, filename='fabindia_kids_products.json')

# for product in products:
#     print(product)