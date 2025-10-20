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

BASE_URL = "https://outfitters.com.pk"
BACKEND_API = "http://localhost:5000/api/products"

categories = {
    "men": "https://outfitters.com.pk/collections/men-end-of-season-sale",
    "men-new-arrival": "https://outfitters.com.pk/collections/men-new-arrivals-view-all",
    "men-t-shirts": "https://outfitters.com.pk/collections/men-t-shirts",
    "men-shirts": "https://outfitters.com.pk/collections/men-shirts",
    "men-polo-shirts": "https://outfitters.com.pk/collections/men-polo-shirts",
    "men-activewear": "https://outfitters.com.pk/collections/men-activewear",
    "men-trousers": "https://outfitters.com.pk/collections/men-trousers",
    "men-shorts": "https://outfitters.com.pk/collections/men-shorts",
    "men-jeans": "https://outfitters.com.pk/collections/men-denim-collection",
    "men-t-shirts-sale": "https://outfitters.com.pk/collections/men-t-shirt-sale",
    "men-polo-sale": "https://outfitters.com.pk/collections/men-polo-sale",
    "men-trousers-sale": "https://outfitters.com.pk/collections/men-trousers-sale",
    "men-jeans-sale": "https://outfitters.com.pk/collections/men-jeans-sale",
    "men-activewear-sale": "https://outfitters.com.pk/collections/men-activewear-sale",
    "men-shirt-sale": "https://outfitters.com.pk/collections/men-shirt-sale",
    "men-shorts-sale": "https://outfitters.com.pk/collections/men-shorts-sale",

    "women-new-arrival": "https://outfitters.com.pk/collections/women-new-arrivals-view-all",
    "women-shirts": "https://outfitters.com.pk/collections/women-shirts",
    "women-t-shirts": "https://outfitters.com.pk/collections/women-t-shirts",
    "women-polos": "https://outfitters.com.pk/collections/women-polos",
    "women-dresses-and-jumpsuits": "https://outfitters.com.pk/collections/women-dresses-and-jumpsuit",
    "women-shirts-and-shorts": "https://outfitters.com.pk/collections/women-skirts-and-shorts",
    "women-jeans": "https://outfitters.com.pk/collections/women-denim-collection",
    "women-trousers": "https://outfitters.com.pk/collections/women-trouser",
    "women-activewear": "https://outfitters.com.pk/collections/women-activewear",
    "women": "https://outfitters.com.pk/collections/women-end-of-season-sale",
    "women-t-shirts-sale": "https://outfitters.com.pk/collections/women-t-shirts-sale",
    "women-shirts-sale": "https://outfitters.com.pk/collections/women-shirts-sale",
    "women-polo-sale": "https://outfitters.com.pk/collections/women-polo-sale",
    "women-shorts-sale": "https://outfitters.com.pk/collections/women-shorts-sale",
    "women-jumpsuits-sale": "https://outfitters.com.pk/collections/dresses-jump-suits-sale",
    "women-activewear-sale": "https://outfitters.com.pk/collections/women-activewear-sale",
    "women-trousers-sale": "https://outfitters.com.pk/collections/women-trousers-sale",
    "women-jeans-sale": "https://outfitters.com.pk/collections/women-jeans-sale",
    
    "baby-girls-shirts": "https://outfitters.com.pk/collections/baby-girls-shirts",
    "baby-girls-t-shirts": "https://outfitters.com.pk/collections/baby-girls-t-shirts",
    "baby-girls-dresses": "https://outfitters.com.pk/collections/baby-girls-dresses",
    "baby-girls-suit": "https://outfitters.com.pk/collections/baby-girls-suit",
    "baby-girls-skirts-and-shorts": "https://outfitters.com.pk/collections/baby-girls-skirts-and-shorts",
    "baby-girls-trousers": "https://outfitters.com.pk/collections/baby-girls-trousers",
    "baby-girls-jeans": "https://outfitters.com.pk/collections/baby-girls-jeans",
    "girls-shirts": "https://outfitters.com.pk/collections/girls-shirts",
    "girls-t-shirts": "https://outfitters.com.pk/collections/girls-t-shirts",
    "girls-dresses-and-jumpsuit": "https://outfitters.com.pk/collections/girls-dresses-and-jumpsuit",
    "girls-suit": "https://outfitters.com.pk/collections/z-girls-suit",
    "girls-skirts": "https://outfitters.com.pk/collections/girls-skirts",
    "girls-trousers": "https://outfitters.com.pk/collections/z-girls-trousers",
    "girls-jeans": "https://outfitters.com.pk/collections/z-girls-jeans",
    "girl-t-shirts-sale": "https://outfitters.com.pk/collections/girl-t-shirts-sale",
    "girl-shirts-sale": "https://outfitters.com.pk/collections/girl-shirts-sale",
    "girl-co-ord-sets-sale": "https://outfitters.com.pk/collections/girl-co-ord-sets-sale",
    "girl-dress-sale": "https://outfitters.com.pk/collections/girl-dress-sale",
    "girls-skirt-and-short-sale": "https://outfitters.com.pk/collections/girls-skirt-and-short-sale",
    "girl-trousers-sale": "https://outfitters.com.pk/collections/girl-trousers-sale",
    "girl-jeans-sale": "https://outfitters.com.pk/collections/girl-jeans-sale",
    "girls-winter-sale": "https://outfitters.com.pk/collections/girls-winter-sale",

    "baby-boy-shirt": "https://outfitters.com.pk/collections/baby-boy-shirt",
    "baby-boy-t-shirt": "https://outfitters.com.pk/collections/baby-boy-t-shirt",
    "baby-boys-suits": "https://outfitters.com.pk/collections/baby-boys-suits",
    "baby-boy-dungaree-1": "https://outfitters.com.pk/collections/baby-boy-dungaree-1",
    "baby-boys-shorts": "https://outfitters.com.pk/collections/toddler-boys-shorts",
    "baby-boy-trousers-1": "https://outfitters.com.pk/collections/baby-boy-trousers-1",
    "baby-boy-jeans": "https://outfitters.com.pk/collections/baby-boy-jeans",
    "juniors-boy-shirts": "https://outfitters.com.pk/collections/juniors-boy-shirts",
    "juniors-boy-t-shirts": "https://outfitters.com.pk/collections/juniors-boy-t-shirts",
    "juniors-boy-co-ord-sets": "https://outfitters.com.pk/collections/juniors-boy-co-ord-sets",
    "junior-boy-shorts": "https://outfitters.com.pk/collections/junior-boy-shorts",
    "junior-boys-trousers": "https://outfitters.com.pk/collections/junior-boys-trousers",
    "juniors-boy-jeans": "https://outfitters.com.pk/collections/juniors-boy-jeans",
    "boy-t-shirts-sale": "https://outfitters.com.pk/collections/boy-t-shirts-sale",
    "boy-shirts-sale": "https://outfitters.com.pk/collections/boy-shirts-sale",
    "boy-co-ord-sets-sale": "https://outfitters.com.pk/collections/boy-co-ord-sets-sale",
    "boys-dungaree-sale": "https://outfitters.com.pk/collections/boys-dungaree-sale",
    "boy-shorts-sale": "https://outfitters.com.pk/collections/boy-shorts-sale",
    "boy-trousers-sale": "https://outfitters.com.pk/collections/boy-trousers-sale",
    "boy-jeans-sale": "https://outfitters.com.pk/collections/boy-jeans-sale",
}

for category, url in categories.items():
    print(f"\nScraping category: {category}")
    driver.get(url)

    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    soup = BeautifulSoup(driver.page_source, "html.parser")
    product_cards = soup.find_all("div", class_="card-wrapper")

    for i, card in enumerate(product_cards):
        info_container = card.find("div", class_="card__information")
        if not info_container:
            continue

        title_tag = info_container.find("h3", class_="card__heading")
        title = title_tag.text.strip() if title_tag else "N/A"

        info_container1 = card.find("div", class_="card-information")

        regular_price_tag = info_container1.find("s", class_="price-item--regular")
        regular_price = (
            regular_price_tag.find("span", class_="money")
            .string.strip()
            .replace("PKR", "")
            .replace(",", "")
            .strip()
            if regular_price_tag and regular_price_tag.find("span", class_="money")
            else "0"
        )

        sale_price_tag = info_container1.find("span", class_="price-item--sale")
        sale_price = (
            sale_price_tag.find("span", class_="money")
            .string.strip()
            .replace("PKR", "")
            .replace(",", "")
            .strip()
            if sale_price_tag and sale_price_tag.find("span", class_="money")
            else "0"
        )

        if sale_price == "0":
            regular_container = info_container1.find("div", class_="price__regular")
            if regular_container:
                regular_price_tag = regular_container.find("span", class_="money")
                regular_price = (
                    regular_price_tag.string.strip()
                    .replace("PKR", "")
                    .replace(",", "")
                    .strip()
                    if regular_price_tag
                    else "0"
                )
                sale_price = regular_price

        discount_badge = info_container1.find("span", class_="sale-badge")
        discount_percentage = discount_badge.string.strip() if discount_badge else "0%"

        image_container = card.find("div", class_="card__inner")
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
        if title_tag and title_tag.a and "href" in title_tag.a.attrs:
            product_url = BASE_URL + title_tag.a["href"]

        product_data = {
            "name": title,
            "brand": "Outfitters",
            "price": (
                float(sale_price) if sale_price.replace(".", "", 1).isdigit() else 0
            ),
            "regular_price": (
                float(regular_price)
                if regular_price.replace(".", "", 1).isdigit()
                else 0
            ),
            "sale_price": (
                float(sale_price) if sale_price.replace(".", "", 1).isdigit() else 0
            ),
            "discount_percentage": discount_percentage,
            "on_sale": sale_price != regular_price
            and sale_price != "0"
            and regular_price != "0",
            "image": image_url,
            "category": category,
            "vendor": {"name": "Outfitters", "url": product_url},
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
