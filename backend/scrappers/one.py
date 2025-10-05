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

BASE_URL = "https://beoneshopone.com"
BACKEND_API = "http://localhost:5000/api/products"

categories = {
    "men": f"{BASE_URL}/collections/men",
    "men-new-arrival": "https://beoneshopone.com/collections/men-new-arrivals-all",
    "men-new-arrival2": "https://beoneshopone.com/collections/men-new-arrivals-all?page=2",
    "men-new-arrival3": "https://beoneshopone.com/collections/men-new-arrivals-all?page=3",
    "men-new-arrival4": "https://beoneshopone.com/collections/men-new-arrivals-all?page=4",
    "men-new-arrival5": "https://beoneshopone.com/collections/men-new-arrivals-all?page=5",
    "men-new-arrival6": "https://beoneshopone.com/collections/men-new-arrivals-all?page=6",
    "men-new-arrival7": "https://beoneshopone.com/collections/men-new-arrivals-all?page=7",
    "men-new-arrival8": "https://beoneshopone.com/collections/men-new-arrivals-all?page=8",
    "men-new-arrival9": "https://beoneshopone.com/collections/men-new-arrivals-all?page=9",
    "men-new-arrival10": "https://beoneshopone.com/collections/men-new-arrivals-all?page=10",
    "men-new-arrival11": "https://beoneshopone.com/collections/men-new-arrivals-all?page=11",
    "men-new-arrival12": "https://beoneshopone.com/collections/men-new-arrivals-all?page=12",
    "men-new-arrival13": "https://beoneshopone.com/collections/men-new-arrivals-all?page=13",
    "men-new-arrival14": "https://beoneshopone.com/collections/men-new-arrivals-all?page=14",
    "men-new-arrival15": "https://beoneshopone.com/collections/men-new-arrivals-all?page=15",
    
    # "women-new-arrival": "https://beoneshopone.com/collections/women-new-arrivals-all",
    # "women-new-arrival2": "https://beoneshopone.com/collections/women-new-arrivals-all?page=2",
    # "women-new-arrival3": "https://beoneshopone.com/collections/women-new-arrivals-all?page=3",
    # "women-new-arrival4": "https://beoneshopone.com/collections/women-new-arrivals-all?page=4",
    # "women-new-arrival5": "https://beoneshopone.com/collections/women-new-arrivals-all?page=5",
    # "women-new-arrival6": "https://beoneshopone.com/collections/women-new-arrivals-all?page=6",
    # "women-new-arrival7": "https://beoneshopone.com/collections/women-new-arrivals-all?page=7",
    # "women-new-arrival8": "https://beoneshopone.com/collections/women-new-arrivals-all?page=8",
    
    # "kids-new-arrival": "https://beoneshopone.com/collections/kids-new-arrivals",
    # "kids-new-arrival2": "https://beoneshopone.com/collections/kids-new-arrivals?page=2",
    # "kids-new-arrival3": "https://beoneshopone.com/collections/kids-new-arrivals?page=3",
    # "kids-new-arrival4": "https://beoneshopone.com/collections/kids-new-arrivals?page=4",
    # "kids-new-arrival5": "https://beoneshopone.com/collections/kids-new-arrivals?page=5",
    # "kids-new-arrival6": "https://beoneshopone.com/collections/kids-new-arrivals?page=6",
    # "kids-new-arrival7": "https://beoneshopone.com/collections/kids-new-arrivals?page=7",
    # "kids-new-arrival8": "https://beoneshopone.com/collections/kids-new-arrivals?page=8",
    # "kids-new-arrival9": "https://beoneshopone.com/collections/kids-new-arrivals?page=9",
    # "kids-new-arrival10": "https://beoneshopone.com/collections/kids-new-arrivals?page=10",
    # "kids-new-arrival11": "https://beoneshopone.com/collections/kids-new-arrivals?page=11",
    # "kids-new-arrival12": "https://beoneshopone.com/collections/kids-new-arrivals?page=12",
    # "kids-new-arrival13": "https://beoneshopone.com/collections/kids-new-arrivals?page=13",
    # "kids-new-arrival14": "https://beoneshopone.com/collections/kids-new-arrivals?page=14",
    # "kids-new-arrival15": "https://beoneshopone.com/collections/kids-new-arrivals?page=15",
    # "kids-new-arrival16": "https://beoneshopone.com/collections/kids-new-arrivals?page=16",
    # "kids-new-arrival17": "https://beoneshopone.com/collections/kids-new-arrivals?page=17",
    
    # "men1": "https://beoneshopone.com/collections/men-tops-polos",
    # "men1-a": "https://beoneshopone.com/collections/men-tops-polos?page=2",
    # "men1-b": "https://beoneshopone.com/collections/men-tops-polos?page=3",
    # "men2": "https://beoneshopone.com/collections/men-tops-t-shirts",
    # "men3": "https://beoneshopone.com/collections/men-tops-casual-shirts",
    # "men4": "https://beoneshopone.com/collections/men-co-ords-sets",
    # "men5": "https://beoneshopone.com/collections/men-bottoms-shorts",
    # "men6": "https://beoneshopone.com/collections/men-bottoms-chinos",
    # "men7": "https://beoneshopone.com/collections/men-bottoms-trouser-chinos",
    # "men8": "https://beoneshopone.com/collections/men-bottoms-jeans",
    # "men9": "https://beoneshopone.com/collections/men-tops-sweaters",
    # "men10": "https://beoneshopone.com/collections/men-sweat-shirt-hoodies",
    # "men11": "https://beoneshopone.com/collections/men-tops-jackets-outerwear",
    # "men12": "https://beoneshopone.com/collections/men-tops-gym-wear-tops",
    # "men13": "https://beoneshopone.com/collections/men-bottoms-gym-wear-bottoms",
    # "men14": "https://beoneshopone.com/collections/men-tops-polos",
    
    # "women": f"{BASE_URL}/collections/women",
    # "women1": "https://beoneshopone.com/collections/women-new-arrivals",
    # "women2": "https://beoneshopone.com/collections/women-tops-t-shirts",
    # "women2-a": "https://beoneshopone.com/collections/women-tops-t-shirts?page=2",
    # "women2-b": "https://beoneshopone.com/collections/women-tops-t-shirts?page=3",
    # "women3": "https://beoneshopone.com/collections/women-tops-dresses",
    # "women4": "https://beoneshopone.com/collections/women-tops-shirts-tops",
    # "women4-a": "https://beoneshopone.com/collections/women-tops-shirts-tops?page=2",
    # "women5": "https://beoneshopone.com/collections/women-bottoms-co-ords-sets",
    # "women5-a": "https://beoneshopone.com/collections/women-bottoms-co-ords-sets?page=2",
    # "women6": "https://beoneshopone.com/collections/women-bottoms-jeans",
    # "women6-a": "https://beoneshopone.com/collections/women-bottoms-jeans?page=2",
    # "women7": "https://beoneshopone.com/collections/women-bottoms-pants-lowers",
    # "women7-a": "https://beoneshopone.com/collections/women-bottoms-pants-lowers?page=2",
    # "women8": "https://beoneshopone.com/collections/women-tops-dungarees-jump-suit",
    # "women9": "https://beoneshopone.com/collections/women-tops-sweaters",
    # "women10": "https://beoneshopone.com/collections/sweat-shirt-hoodies",
    # "women10-a": "https://beoneshopone.com/collections/sweat-shirt-hoodies?page=2",
    # "women11": "https://beoneshopone.com/collections/women-tops-jackets-outerwear",
    # "women12": "https://beoneshopone.com/collections/women-gym-wear",
    # "women13": "https://beoneshopone.com/collections/women-new-arrivals-luxe",
    # "women14": "https://beoneshopone.com/collections/women-luxe-shirts-tops",
    # "women15": "https://beoneshopone.com/collections/women-luxe-dresses",
    # "women16": "https://beoneshopone.com/collections/women-luxe-jump-suits",
    # "women17": "https://beoneshopone.com/collections/women-luxe-pants-lowers",
    # "women18": "https://beoneshopone.com/collections/swim-suit-women",
    
    # "boys1": "https://beoneshopone.com/collections/boys-new-arrivals",
    # "boys2": "https://beoneshopone.com/collections/boys-t-shirts",
    # "boys3": "https://beoneshopone.com/collections/boys-casual-shirts",
    # "boys4": "https://beoneshopone.com/collections/boys-polo",
    # "boys5": "https://beoneshopone.com/collections/boys-shorts",
    # "boys6": "https://beoneshopone.com/collections/boys-co-ords-sets",
    # "boys7": "https://beoneshopone.com/collections/boys-trousers",
    # "boys8": "https://beoneshopone.com/collections/boys-jeans",
    # "boys9": "https://beoneshopone.com/collections/boys-night-suit",
    # "boys10": "https://beoneshopone.com/collections/boys-sweaters",
    # "boys11": "https://beoneshopone.com/collections/boys-sweat-shirt-hoodies",
    # "boys12": "https://beoneshopone.com/collections/boys-jackets-outerwear",
    # "boys13": "https://beoneshopone.com/collections/swimwear-boys",
    # "boys14": "https://beoneshopone.com/collections/boys-new-arrivals",
    
    # "girls1": "https://beoneshopone.com/collections/girls-new-arrivals",
    # "girls2": "https://beoneshopone.com/collections/girls-shirts-tops",
    # "girls3": "https://beoneshopone.com/collections/girls-co-ords-sets",
    # "girls4": "https://beoneshopone.com/collections/girls-dresses",
    # "girls5": "https://beoneshopone.com/collections/girls-t-shirts",
    # "girls6": "https://beoneshopone.com/collections/girls-skirts",
    # "girls7": "https://beoneshopone.com/collections/girls-dungarees-jumpsuits",
    # "girls8": "https://beoneshopone.com/collections/girls-jeans",
    # "girls9": "https://beoneshopone.com/collections/girls-pants-lowers",
    # "girls10": "https://beoneshopone.com/collections/girls-night-wear",
    # "girls11": "https://beoneshopone.com/collections/girls-sweaters",
    # "girls12": "https://beoneshopone.com/collections/girls-jackets-outerwear",
    # "girls13": "https://beoneshopone.com/collections/girls-sweat-shirt-hoodies",
    
    # "men-sale": "https://beoneshopone.com/collections/flat-50-men",
    # "women-sale": "https://beoneshopone.com/collections/flat-50-women",
    # "kids-sale": "https://beoneshopone.com/collections/flat-50-new-kids",
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
        info_container = card.find("div", class_="grid-product__content")
        if not info_container:
            continue

        title_tag = info_container.find(
            "div", class_="grid-product__title grid-product__title--body"
        )
        title = title_tag.text.strip() if title_tag else "N/A"

        price_tag = info_container.find("span", class_="money")
        price_text = (
            price_tag.text.strip().replace("Rs.", "").replace(",", "").strip()
            if price_tag
            else "0"
        )

        installment_price_tag = info_container.find("span", class_="price-divide")
        installment_price_text = (
            installment_price_tag.text.strip().replace(",", "").strip()
            if installment_price_tag
            else "0"
        )

        try:
            price = float(price_text)
        except:
            price = 0

        try:
            installment_price = float(installment_price_text)
        except:
            installment_price = 0

        image_container = info_container.find("div", class_="grid__item-image-wrapper")
        image_url = None
        if (
            image_container
            and image_container.img
            and "src" in image_container.img.attrs
        ):
            image_url = image_container.img["src"]
            if image_url.startswith("//"):
                image_url = "https:" + image_url

        product_url = "N/A"
        if image_container and image_container.a and "href" in image_container.a.attrs:
            product_url = BASE_URL + image_container.a["href"]

        product_data = {
            "name": title,
            "brand": "BeOne ShopOne",
            "price": price,
            "installment_price": installment_price,
            "currency": "Rs.",
            "image": image_url,
            "category": category,
            "vendor": {"name": "BeOne ShopOne", "url": product_url},
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
