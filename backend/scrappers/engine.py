import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)

BASE_URL = "https://engine.com.pk"
BACKEND_API = "http://localhost:5000/api/products"

categories = {
    # "men": f"{BASE_URL}/collections/men",
    # "men-p2": f"{BASE_URL}/collections/men?page=2",
    # "men-p3": f"{BASE_URL}/collections/men?page=3",
    # "men-p4": f"{BASE_URL}/collections/men?page=4",
    # "men-p5": f"{BASE_URL}/collections/men?page=5",
    # "men-p6": f"{BASE_URL}/collections/men?page=6",
    # "men-p7": f"{BASE_URL}/collections/men?page=7",
    # "men-p8": f"{BASE_URL}/collections/men?page=8",
    # "men-p9": f"{BASE_URL}/collections/men?page=9",
    # "men-p10": f"{BASE_URL}/collections/men?page=10",
    "men-p11": f"{BASE_URL}/collections/men?page=11",
    "men-p12": f"{BASE_URL}/collections/men?page=12",
    "men-p13": f"{BASE_URL}/collections/men?page=13",
    "men-p14": f"{BASE_URL}/collections/men?page=14",
    "men-p15": f"{BASE_URL}/collections/men?page=15",
    "men1": f"{BASE_URL}/collections/men-tshirts",
    "men2": f"{BASE_URL}/collections/men-polo-shirt",
    "men3": f"{BASE_URL}/collections/men-casual-shirt",
    "men4": f"{BASE_URL}/collections/new-arrivals",
    "men5": f"{BASE_URL}/collections/green-week-sale",
    # "men6": f"{BASE_URL}/collections/men-sale",
    # "men7": f"{BASE_URL}/collections/women-sale",
    # "men8": f"{BASE_URL}/collections/kids-sale",
    # "men9": f"{BASE_URL}/collections/men-tops",
    # "men10": f"{BASE_URL}/collections/button-down",
    # "men11": f"{BASE_URL}/collections/men-jeans",
    # "men12": f"{BASE_URL}/collections/men-vests",
    # "men13": f"{BASE_URL}/collections/men-active-wear",
    # "men14": f"{BASE_URL}/collections/men-bottoms",
    # "men15": f"{BASE_URL}/collections/men-shorts",
    # "men16": f"{BASE_URL}/collections/men-trouser",
    # "men17": f"{BASE_URL}/collections/men-suits",
    # "men18": f"{BASE_URL}/collections/men-pant",
    # "men19": f"{BASE_URL}/collections/women-tops",
    # "men20": f"{BASE_URL}/collections/women-bottoms",
    # "men21": f"{BASE_URL}/collections/women-denims",
    # "men22": f"{BASE_URL}/collections/women-trousers",
    # "men23": f"{BASE_URL}/collections/women-tights",
    # "men24": f"{BASE_URL}/collections/women-casual-shirt",
    # "men25": f"{BASE_URL}/collections/women-dress",
    # "men26": f"{BASE_URL}/collections/women-suits",
    # "men27": f"{BASE_URL}/collections/women-tees",
    # "men28": f"{BASE_URL}/collections/women-active-wear",
    
    # "women-p2": f"{BASE_URL}/collections/women?page=2",
    # "women-p3": f"{BASE_URL}/collections/women?page=3",
    # "women-p4": f"{BASE_URL}/collections/women?page=4",
    # "women-p5": f"{BASE_URL}/collections/women?page=5",
    # "women1": f"{BASE_URL}/collections/men-new-arrivals",
    # "women2": f"{BASE_URL}/collections/women-new-arrivals",
    # "women3": f"{BASE_URL}/collections/juniornew",
    # "women4": f"{BASE_URL}/collections/baby-boys",
    # "women5": f"{BASE_URL}/collections/junior-boys",
    # "women6": f"{BASE_URL}/collections/junior-girls",
    # "women7": f"{BASE_URL}/collections/baby-girl-tops",
    # "women8": f"{BASE_URL}/collections/baby-girls-suits",
    # "women9": f"{BASE_URL}/collections/baby-girl-shorts",
    # "women10": f"{BASE_URL}/collections/baby-girls-pants",
    # "women11": f"{BASE_URL}/collections/baby-girl-jeans",
    # "women12": f"{BASE_URL}/collections/girl-knit-top-big",
    # "women13": f"{BASE_URL}/collections/girls-suit",
    # "women14": f"{BASE_URL}/collections/junior-girl-jeans",
    # "women15": f"{BASE_URL}/collections/junior-girl-pants",
    # "women16": f"{BASE_URL}/collections/junior-girl-tights",
    # "women17": f"{BASE_URL}/collections/junior-boys",
    # "women18": f"{BASE_URL}/collections/junior-boy-t-shirt",
    # "women19": f"{BASE_URL}/collections/junior-boy-shorts",
    # "women20": f"{BASE_URL}/collections/junior-boy-jeans",
    # "women21": f"{BASE_URL}/collections/junior-boy-trouser",
    # "women22": f"{BASE_URL}/collections/junior-boy-pants",
    # "women23": f"{BASE_URL}/collections/boys-t-shirts-small",
    # "women24": f"{BASE_URL}/collections/baby-boy-shirt",
    # "women25": f"{BASE_URL}/collections/baby-boys-shorts",
    # "women26": f"{BASE_URL}/collections/junior-boy-pants",
    # "women27": f"{BASE_URL}/collections/baby-boy-pant",
    # "women28": f"{BASE_URL}/collections/boys-suit-small",
}


total_products_scraped = 0

for category, url in categories.items():
    print(f"\nScraping category: {category}")
    driver.get(url)

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.o-product-thumbnail"))
        )
    except Exception:
        print(f"No products found in {category}")
        continue

    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    soup = BeautifulSoup(driver.page_source, "html.parser")
    product_cards = soup.select("a.o-product-thumbnail")
    print(f"Found {len(product_cards)} products in {category}")

    for i, card in enumerate(product_cards, start=1):
        title_tag = card.find("p", class_="o-product-thumbnail__title")
        title = title_tag.get_text(strip=True) if title_tag else "N/A"

        price_tag = card.find("span", class_="o-pricing__money.o-pricing__price")
        if not price_tag:
            price_tag = card.find("span", class_="o-pricing__price")
        price_text = (
            price_tag.get_text(strip=True).replace("PKR", "").replace(",", "")
            if price_tag
            else "0"
        )
        try:
            price = float(price_text)
        except:
            price = 0

        product_url = BASE_URL + card.get("href", "")

        image_tag = card.find("img")
        image_url = (
            "https:" + image_tag["src"] if image_tag and image_tag.get("src") else None
        )

        product_data = {
            "name": title,
            "brand": "Engine",
            "price": price,
            "image": image_url,
            "category": category,
            "vendor": {"name": "Engine", "url": product_url},
        }

        try:
            resp = requests.post(
                BACKEND_API,
                headers={"Content-Type": "application/json"},
                json=product_data,
                timeout=15,
            )
            if resp.status_code == 201:
                print(f"Uploaded: {title}")
            else:
                print(f"Failed ({resp.status_code}): {resp.text}")
        except Exception as e:
            print(f"Error uploading {title}: {e}")

        total_products_scraped += 1

driver.quit()
print(f"\nDONE Total products processed: {total_products_scraped}")
