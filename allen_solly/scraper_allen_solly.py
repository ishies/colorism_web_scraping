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
    product_elements = soup.find_all('div', class_='ProductCard_productCard__T2sam.productCard.ProductCard_AS__S6Kh_.undefined')

    print(f"Found {len(product_elements)} products.")

    for i, product in enumerate(product_elements):
        product_info = {}

        # Extract Image
        image_element = product.find('img')
        product_info['image'] = image_element.get('src') if image_element else None

        # Extract Name
        name_element = product.select_one('div.ProductCard_description__BQzle')
        product_info['name'] = name_element.text.strip() if name_element else None   

        # Extract Price
        price_element = product.find('span', class_='price')
        if price_element:
            price_str = price_element.text.strip()
            # Extract the numerical value from the price string
            price_str = ''.join(filter(str.isdigit, price_str))
            decimal_price = decimal.Decimal(price_str)
            product_info['price'] = float(decimal_price)
        else:
            product_info['price'] = None

        product_info['index'] = i
        products.append(product_info)
    
    return products

def save_to_json(products, filename='allen_solly_women_products.json'):
    try:
        # Load existing data from the JSON file
        with open(filename, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
            print(f"Loaded existing data: {existing_data}")
    except FileNotFoundError:
        existing_data = []
        print("File not found, initializing new data.")

    # Append new products to the existing data
    existing_data.extend(products)

    # Write back to the JSON file
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)
        print(f"Saved {len(products)} products to {filename}")

    print(f"Final data in file: {existing_data}")

# URL to scrape
urls = [
    'https://allensolly.abfrl.in/c/new-arrivals?page=1&orderby=popular&orderway=asc&fp[]=Gender__fq%3AWomen',
    # Add more URLs if needed
]

all_products = []

# Scrape the products
for url in urls:
    products = scrape_fabindia_products(url)
    all_products.extend(products)

save_to_json(all_products, filename='allen_solly_women_products.json')

for product in all_products:
    print(product)