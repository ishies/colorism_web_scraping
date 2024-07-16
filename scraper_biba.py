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

def get_all_page_content(url, driver):
    driver.get(url)

    # Scroll down several times to load all products
    for _ in range(10):  # Adjust the number of scrolls as needed
        scroll_to_bottom(driver)

    try:
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'col-6.col-sm-6.col-md-3')))
    except Exception as e:
        print(e)
    
    # Wait briefly for content to load after scrolling
    time.sleep(5)  # Adjust sleep time as needed

    # Get the page source after all content is loaded
    page_content = driver.page_source

    return page_content

def scrape_products_from_url(url, driver):
    page_content = get_all_page_content(url, driver)
    soup = BeautifulSoup(page_content, 'html.parser')

    products = []

    # Find all elements
    product_elements = soup.find_all('div', class_='col-6.col-sm-6.col-md-3')
    i = 0
    for product in product_elements:
        product_info = {}

        image_element = product.find('img')
        product_info['image'] = image_element['src'] if image_element else None

        # Extract Other Info
        name_element = product.find('a', class_='link.d-lg-none') 
        product_info['name'] = name_element.text.strip() if name_element else None   

        price_element = product.find('span', class_='sales')
        price_str = price_element.text.strip() if price_element else None
        cleaned_price_str = price_str.replace('$', '').replace(',', '').strip()
        decimal_price = decimal.Decimal(cleaned_price_str)
        product_info['price'] = float(decimal_price)

        product_info['index'] = i
        i += 1

        products.append(product_info)
    
    return products

def scrape_products_from_multiple_urls(urls):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    all_products = []
    for url in urls:
        products = scrape_products_from_url(url, driver)
        all_products.extend(products)

    driver.quit()
    return all_products

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

# List of URLs to scrape
urls_to_scrape = [
    'https://www.biba.in/intl/suit-sets/straight-suit-sets/',
    'https://www.biba.in/intl/suit-sets/anarkali-suit-sets/',
    'https://www.biba.in/intl/suit-sets/flared-suit-sets/',
    'https://www.biba.in/intl/suit-sets/a-line-and-kalidar-suits/',
    'https://www.biba.in/intl/suit-sets/asymmetric-suits/',
    'https://www.biba.in/intl/kurtas-and-tops/kurtas/',
    'https://www.biba.in/intl/kurtas-and-tops/kurtis-and-tops/',
    'https://www.biba.in/intl/dresses/casual/',
    'https://www.biba.in/intl/dresses/autumn-winter/',
    'https://www.biba.in/intl/bottomwear/churidar-and-leggings/',
    'https://www.biba.in/intl/bottomwear/palazzos/',
    'https://www.biba.in/intl/bottomwear/pants/',
    # Add more URLs as needed
]

# Scrape products from multiple URLs
products = scrape_products_from_multiple_urls(urls_to_scrape)

# Save products to JSON file
save_to_json(products, filename='biba_products.json')

# Print the scraped products (optional)
for product in products:
    print(product)