import os
import time
import requests
from selenium import webdriver
from bs4 import BeautifulSoup

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

BASE_URL = "https://www.cougar.com.pk"
BACKEND_API = "http://localhost:5000/api/products"

categories = {
    "men": "https://www.cougar.com.pk/collections/men",
    "men-polo": "https://www.cougar.com.pk/collections/men-polo-shirts",
    "men-t-shirts": "https://www.cougar.com.pk/collections/men-t-shirts",
    "men-shirts": "https://www.cougar.com.pk/collections/men-casual-shirts",
    "men-tank-tops": "https://www.cougar.com.pk/collections/men-tank-tops",
    "men-activewear": "https://www.cougar.com.pk/collections/men-activewear",
    "men-trousers": "https://www.cougar.com.pk/collections/men-trousers",
    "men-jeans": "https://www.cougar.com.pk/collections/men-jeans",
    "men-pants": "https://www.cougar.com.pk/collections/men-pants",
    "men-shorts": "https://www.cougar.com.pk/collections/men-shorts",
    "men-jacket": "https://www.cougar.com.pk/collections/men-jackets",
    "men-sweaters": "https://www.cougar.com.pk/collections/men-sweaters",
    "men-hoodies": "https://www.cougar.com.pk/collections/men-hoodies",
    "men-sweatshirts": "https://www.cougar.com.pk/collections/men-sweatshirts",
    "men-sale": "https://www.cougar.com.pk/collections/men-sale",
    "men-polo-sale": "https://www.cougar.com.pk/collections/men-polo-sale",
    "men-t-shirts-sale": "https://www.cougar.com.pk/collections/men-t-shirts-sale",
    "men-shirts-sale": "https://www.cougar.com.pk/collections/men-casual-shirts-sale",
    "men-tank-tops-sale": "https://www.cougar.com.pk/collections/men-tank-tops-sale",
    "men-activewear-sale": "https://www.cougar.com.pk/collections/men-activewear-sale",
    "men-trousers-sale": "https://www.cougar.com.pk/collections/men-trousers-sale",
    "men-jeans-sale": "https://www.cougar.com.pk/collections/men-jeans-sale",
    "men-pants-sale": "https://www.cougar.com.pk/collections/men-pants-sale",
    "men-shorts-sale": "https://www.cougar.com.pk/collections/men-shorts-sale",
    "men-jacket-sale": "https://www.cougar.com.pk/collections/men-jackets-sale",
    "men-sweaters-sale": "https://www.cougar.com.pk/collections/men-sweaters-sale",
    "men-hoodies-sale": "https://www.cougar.com.pk/collections/men-hoodies-sale",
    "men-sweatshirts-sale": "https://www.cougar.com.pk/collections/men-sweatshirts-sale",
    
    "women": "https://www.cougar.com.pk/collections/women",
    "women-tops": "https://www.cougar.com.pk/collections/women-tops",
    "women-t-shirts": "https://www.cougar.com.pk/collections/women-t-shirts",
    "women-shirts": "https://www.cougar.com.pk/collections/women-shirts",
    "women-dresses": "https://www.cougar.com.pk/collections/women-dresses",
    "women-activewear": "https://www.cougar.com.pk/collections/women-activewear",
    "women-trousers": "https://www.cougar.com.pk/collections/women-trousers",
    "women-jeans": "https://www.cougar.com.pk/collections/women-jeans",
    "women-jumpsuits": "https://www.cougar.com.pk/collections/women-jumpsuits",
    "women-camisoles": "https://www.cougar.com.pk/collections/women-camisoles",
    "women-jacket": "https://www.cougar.com.pk/collections/women-jackets",
    "women-sweaters": "https://www.cougar.com.pk/collections/women-sweaters",
    "women-hoodies": "https://www.cougar.com.pk/collections/women-hoodies",
    "women-sweatshirts": "https://www.cougar.com.pk/collections/women-sweatshirts",
    "women-co-ords": "https://www.cougar.com.pk/collections/women-co-ord-sets",
    "women-coats": "https://www.cougar.com.pk/collections/women-coats",
    "women-sale": "https://www.cougar.com.pk/collections/women-sale",
    "women-tops-sale": "https://www.cougar.com.pk/collections/women-tops-sale",
    "women-t-shirts-sale": "https://www.cougar.com.pk/collections/women-t-shirts-sale",
    "women-shirts-sale": "https://www.cougar.com.pk/collections/women-shirts-sale",
    "women-dresses-sale": "https://www.cougar.com.pk/collections/women-dresses-sale",
    "women-activewear-sale": "https://www.cougar.com.pk/collections/women-activewear-sale",
    "women-trousers-sale": "https://www.cougar.com.pk/collections/women-trousers-sale",
    "women-jeans-sale": "https://www.cougar.com.pk/collections/women-jeans-sale",
    "women-jumpsuits-sale": "https://www.cougar.com.pk/collections/women-jumpsuits-sale",
    "women-camisoles-sale": "https://www.cougar.com.pk/collections/women-camisoles-sale",
    "women-jacket-sale": "https://www.cougar.com.pk/collections/women-jackets-sale",
    "women-sweaters-sale": "https://www.cougar.com.pk/collections/women-sweaters-sale",
    "women-hoodies-sale": "https://www.cougar.com.pk/collections/women-hoodie-sale",
    "women-sweatshirts-sale": "https://www.cougar.com.pk/collections/women-sweatshirts-sale",
    "women-co-ords-sale": "https://www.cougar.com.pk/collections/women-co-ord-sets-sale",
    "women-coats-sale": "https://www.cougar.com.pk/collections/women-coats-sale",
    
    "boys": "https://www.cougar.com.pk/collections/boys",
    "boys-polo": "https://www.cougar.com.pk/collections/boys-polos",
    "boys-t-shirts": "https://www.cougar.com.pk/collections/boys-t-shirts",
    "boys-shirts": "https://www.cougar.com.pk/collections/boys-shirts",
    "boys-trousers": "https://www.cougar.com.pk/collections/boys-trousers",
    "boys-jeans": "https://www.cougar.com.pk/collections/boys-jeans",
    "boys-pants": "https://www.cougar.com.pk/collections/boys-pants",
    "boys-shorts": "https://www.cougar.com.pk/collections/boys-shorts",
    "boys-jacket": "https://www.cougar.com.pk/collections/boys-jackets",
    "boys-sweaters": "https://www.cougar.com.pk/collections/boys-sweaters",
    "boys-hoodies": "https://www.cougar.com.pk/collections/boys-hoodies",
    "boys-sweatshirts": "https://www.cougar.com.pk/collections/boys-sweatshirts",
    "boys-sale": "https://www.cougar.com.pk/collections/boys-sale",
    "boys-polo-sale": "https://www.cougar.com.pk/collections/boys-polos-sale",
    "boys-t-shirts-sale": "https://www.cougar.com.pk/collections/boys-t-shirts-sale",
    "boys-shirts-sale": "https://www.cougar.com.pk/collections/boys-shirts-sale",
    "boys-trousers-sale": "https://www.cougar.com.pk/collections/boys-trousers-sale",
    "boys-jeans-sale": "https://www.cougar.com.pk/collections/boys-jeans-sale",
    "boys-pants-sale": "https://www.cougar.com.pk/collections/boys-pants-sale",
    "boys-shorts-sale": "https://www.cougar.com.pk/collections/boys-shorts-sale",
    "boys-jacket-sale": "https://www.cougar.com.pk/collections/boys-jackets-sale",
    "boys-sweaters-sale": "https://www.cougar.com.pk/collections/boys-sweaters-sale",
    "boys-hoodies-sale": "https://www.cougar.com.pk/collections/boys-hoodies-sale",
    "boys-sweatshirts-sale": "https://www.cougar.com.pk/collections/boys-sweatshirts-sale",
    
    "girls": "https://www.cougar.com.pk/collections/girls",
    "girls-tops": "https://www.cougar.com.pk/collections/women-tops",
    "girls-t-shirts": "https://www.cougar.com.pk/collections/women-t-shirts",
    "girls-bottoms": "https://www.cougar.com.pk/collections/girls-bottoms",
    "girls-jumpsuits": "https://www.cougar.com.pk/collections/women-jumpsuits",
    "girls-camisoles": "https://www.cougar.com.pk/collections/women-camisoles",
    "girls-jacket": "https://www.cougar.com.pk/collections/women-jackets",
    "girls-sweaters": "https://www.cougar.com.pk/collections/women-sweaters",
    "girls-hoodies": "https://www.cougar.com.pk/collections/women-hoodies",
    "girls-sweatshirts": "https://www.cougar.com.pk/collections/women-sweatshirts",
    "girls-co-ords": "https://www.cougar.com.pk/collections/women-co-ord-sets",
    "girls-sale": "https://www.cougar.com.pk/collections/girls-sale",
    "girls-tops-sale": "https://www.cougar.com.pk/collections/girls-tops-sale",
    "girls-t-shirts-sale": "https://www.cougar.com.pk/collections/girls-t-shirts-sale",
    "girls-bottoms-sale": "https://www.cougar.com.pk/collections/girls-bottoms-sale",
    "girls-jumpsuits-sale": "https://www.cougar.com.pk/collections/girls-jumpsuits-sale",
    "girls-camisoles-sale": "https://www.cougar.com.pk/collections/girls-camisoles-sale",
    "girls-jacket-sale": "https://www.cougar.com.pk/collections/girls-jackets-sale",
    "girls-sweaters-sale": "https://www.cougar.com.pk/collections/girls-sweaters-sale",
    "girls-hoodies-sale": "https://www.cougar.com.pk/collections/girls-hoodies-sale",
    "girls-sweatshirts-sale": "https://www.cougar.com.pk/collections/girls-sweatshirts-sale",
    "girls-co-ords-sale": "https://www.cougar.com.pk/collections/girls-co-ord-sets-sale",
}

for category, url in categories.items():
    print(f"\nScraping category: {category}")
    driver.get(url)

    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(10):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    soup = BeautifulSoup(driver.page_source, "html.parser")
    product_cards = soup.find_all("div", class_="card-wrapper")

    for i, card in enumerate(product_cards):
        title_tag = card.find("h3", class_="card__heading")
        title = title_tag.text.strip() if title_tag else "N/A"

        regular_price_tag = card.find("s", class_="price-item--regular")
        sale_price_tag = card.find("span", class_="price-item--sale")

        price_tag = sale_price_tag if sale_price_tag else card.find("span", class_="price-item--regular")
        price = (
            price_tag.text.strip().replace("Rs.", "").replace(",", "").strip()
            if price_tag
            else "0"
        )

        product_url = "N/A"
        url_tag = card.find("a", class_="full-unstyled-link")
        if url_tag and "href" in url_tag.attrs:
            product_url = BASE_URL + url_tag["href"]

        img_tag = card.find("img", class_="motion-reduce main-featured-media")
        image_url = None
        if img_tag and "src" in img_tag.attrs:
            image_url = img_tag["src"]
            if image_url.startswith("//"):
                image_url = "https:" + image_url

        product_data = {
            "name": title,
            "brand": "Cougar",
            "price": float(price) if price.replace(".", "", 1).isdigit() else 0,
            "image": image_url,
            "category": category,
            "vendor": {"name": "Cougar", "url": product_url},
            "currency": "Rs."
        }

        try:
            response = requests.post(
                BACKEND_API,
                headers={"Content-Type": "application/json"},
                json=product_data,
            )
            if response.status_code == 201:
                print(f"Uploaded: {title}")
            else:
                print(f"Failed ({response.status_code}): {response.text}")
        except Exception as e:
            print(f"Error uploading product {title}: {e}")

driver.quit()
print("\nScraping finished! All products sent to backend.")
