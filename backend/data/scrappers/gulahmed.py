import os
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.gulahmedshop.com"
BACKEND_API = "http://localhost:5000/api/products"

CATEGORIES = {
    "womens-unstitched": f"{BASE_URL}/unstitched-fabric",
    "womens-pret": f"{BASE_URL}/women/ideas-pret",
    "mens-unstitched": f"{BASE_URL}/mens-clothes/unstitched",
    "mens-pret": f"{BASE_URL}/mens-clothes/pret",
    "ideas-home": f"{BASE_URL}/ideas-home",
    "sale": f"{BASE_URL}/sale",
}


total_products_scraped = 0

for category, url in CATEGORIES.items():
    print(f"\nStarting scraping for category: {category} -> {url}")
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
    except requests.exceptions.RequestException as e:
        print(f"Could not fetch the page {url}: {e}")
        continue

    product_items = soup.find_all("li", class_="product-item")

    if not product_items:
        print("  No product items found on this page. Check the URL or selectors.")
        continue

    for idx, item in enumerate(product_items):
        title_tag = item.find("span", class_="product-item-link")
        title = title_tag.get_text(strip=True) if title_tag else "N/A"

        url_tag = item.find("a", class_="product-item-link")
        product_url = url_tag["href"] if url_tag and "href" in url_tag.attrs else "N/A"

        price_tag = item.find(
            "span", class_="price-wrapper", attrs={"data-price-type": "finalPrice"}
        )
        price_text = (
            price_tag.get_text(strip=True).replace("PKR", "").replace(",", "").strip()
            if price_tag
            else "0"
        )

        regular_price_tag = item.find(
            "span", class_="price-wrapper", attrs={"data-price-type": "oldPrice"}
        )
        regular_price_text = (
            regular_price_tag.get_text(strip=True)
            .replace("PKR", "")
            .replace(",", "")
            .strip()
            if regular_price_tag
            else price_text
        )
        discount_tag = item.find("span", class_="label-content")
        discount_percentage = (
            discount_tag.get_text(strip=True) if discount_tag else "0% OFF"
        )

        try:
            price = float(price_text)
        except:
            price = 0

        try:
            regular_price = float(regular_price_text)
        except:
            regular_price = price

        image_tag = item.find("img", class_="product-image-photo")
        image_url = image_tag["src"] if image_tag and "src" in image_tag.attrs else None
        if image_url and image_url.startswith("//"):
            image_url = "https:" + image_url

        product_data = {
            "name": title,
            "brand": "GulAhmed",
            "price": price,
            "regular_price": regular_price,
            "discount": discount_percentage,
            "image": image_url,
            "category": category,
            "vendor": {"name": "GulAhmed", "url": product_url},
            "currency": "PKR",
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

print(f"\nScraping finished. Total products processed: {total_products_scraped}")
