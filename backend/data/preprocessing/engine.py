import pandas as pd
import numpy as np
import re

# Load the data
print("Loading Engine data...")
df = pd.read_csv("../old/engine.csv")
print(f"Original data: {df.shape}")

# 1. Clean Price Columns
print("Cleaning prices...")


def clean_price_value(price_str):
    if pd.isna(price_str):
        return np.nan
    # Convert to string and remove PKR, commas, and any other characters
    price_str = str(price_str)
    # Remove PKR and any currency symbols
    price_str = (
        price_str.replace("PKR", "")
        .replace("Rs.", "")
        .replace("Rs", "")
        .replace("₹", "")
        .replace("$", "")
    )
    # Remove commas and any other non-numeric characters except decimal point
    price_str = "".join(char for char in price_str if char.isdigit() or char == ".")
    # Convert to float, return NaN if empty
    if price_str == "":
        return np.nan
    try:
        return float(price_str)
    except:
        return np.nan


# Apply cleaning to all price columns
for col in ["price", "original_price", "sale_price"]:
    df[f"{col}_clean"] = df[col].apply(clean_price_value)

# Fill missing original prices
df["original_price_clean"] = df["original_price_clean"].fillna(df["price_clean"])
df["sale_price_clean"] = df["sale_price_clean"].fillna(df["price_clean"])

# 2. Clean Discount Column
print("Cleaning discounts...")


def clean_discount(discount):
    if pd.isna(discount):
        return 0
    discount_str = str(discount)
    # Handle multi-line discount values
    if "%" in discount_str:
        # Extract the percentage number
        discount_pct = "".join(
            char for char in discount_str if char.isdigit() or char == "."
        )
        if discount_pct:
            return float(discount_pct) / 100
    return 0


df["discount_clean"] = df["discount"].apply(clean_discount)

# 3. Product ID
print("Extracting product IDs...")
df["product_id"] = df["product_url"].str.extract(r"products/([^/?]+)")

# 4. Product Type Categorization
print("Categorizing products...")


def get_product_type(title):
    title_lower = str(title).lower()

    type_mapping = {
        "t shirt": "T-Shirts",
        "t-shirt": "T-Shirts",
        "tee": "T-Shirts",
        "polo": "Polos",
        "polo tee": "Polos",
        "shirt": "Shirts",
        "button down": "Shirts",
        "casual shirt": "Shirts",
        "trouser": "Pants",
        "pant": "Pants",
        "chino": "Pants",
        "jeans": "Pants",
        "denim": "Denim",
        "short": "Shorts",
        "suit": "Suits",
        "blazer": "Suits",
        "sweater": "Sweaters",
        "sweat": "Sweaters",
        "hoodie": "Sweaters",
        "jacket": "Jackets",
        "gilet": "Jackets",
        "bomber": "Jackets",
        "sneaker": "Footwear",
        "boot": "Footwear",
        "shoe": "Footwear",
        "sock": "Socks",
        "sweatshirt": "Sweatshirts",
        "henley": "Henleys",
        "active wear": "Activewear",
        "gym": "Activewear",
        "dress": "Dresses",
    }

    for key, value in type_mapping.items():
        if key in title_lower:
            return value

    return "Other"


df["product_type"] = df["title"].apply(get_product_type)

# 5. Extract Primary Color from Variant
print("Extracting primary colors...")


def extract_primary_color(variant):
    if pd.isna(variant):
        return "Not Specified"

    variant_str = str(variant).lower()
    color_mapping = {
        "white": "White",
        "wht": "White",
        "off white": "Off White",
        "owt": "Off White",
        "black": "Black",
        "blk": "Black",
        "jet black": "Black",
        "jbl": "Black",
        "grey": "Grey",
        "gry": "Grey",
        "dark grey": "Dark Grey",
        "dgy": "Dark Grey",
        "light grey": "Light Grey",
        "lgy": "Light Grey",
        "h grey": "Heather Grey",
        "hgy": "Heather Grey",
        "navy": "Navy",
        "nvy": "Navy",
        "dark navy": "Dark Navy",
        "dny": "Dark Navy",
        "blue": "Blue",
        "blu": "Blue",
        "light blue": "Light Blue",
        "lbl": "Light Blue",
        "sky blue": "Sky Blue",
        "skb": "Sky Blue",
        "royal blue": "Royal Blue",
        "rbl": "Royal Blue",
        "brown": "Brown",
        "brn": "Brown",
        "dark brown": "Dark Brown",
        "dbr": "Dark Brown",
        "light brown": "Light Brown",
        "lbn": "Light Brown",
        "dull brown": "Dull Brown",
        "dbn": "Dull Brown",
        "beige": "Beige",
        "bge": "Beige",
        "dull beige": "Dull Beige",
        "dbg": "Dull Beige",
        "green": "Green",
        "grn": "Green",
        "dark green": "Dark Green",
        "dgr": "Dark Green",
        "sage green": "Sage Green",
        "sgn": "Sage Green",
        "olive": "Olive",
        "olv": "Olive",
        "maroon": "Maroon",
        "mrn": "Maroon",
        "red": "Red",
        "rust": "Rust",
        "rst": "Rust",
        "pink": "Pink",
        "pnk": "Pink",
        "burnt pink": "Burnt Pink",
        "brp": "Burnt Pink",
        "khaki": "Khaki",
        "khk": "Khaki",
        "light khaki": "Light Khaki",
        "lkh": "Light Khaki",
        "mustard": "Mustard",
        "mst": "Mustard",
        "orange": "Orange",
        "org": "Orange",
        "yellow": "Yellow",
        "yel": "Yellow",
        "purple": "Purple",
        "prp": "Purple",
        "teal": "Teal",
        "tel": "Teal",
        "aqua": "Aqua",
        "aqu": "Aqua",
        "charcoal": "Charcoal",
        "chr": "Charcoal",
        "camel": "Camel",
        "cml": "Camel",
        "cream": "Cream",
        "crm": "Cream",
        "sand": "Sand",
        "snd": "Sand",
        "dune": "Dune",
        "dne": "Dune",
        "steel": "Steel",
        "stl": "Steel",
        "mix": "Mixed Colors",
        "multi": "Mixed Colors",
    }

    for color_key, color_value in color_mapping.items():
        if color_key in variant_str:
            return color_value

    return "Other"


df["primary_color"] = df["variant"].apply(extract_primary_color)

# 6. Material Type
print("Extracting material types...")


def extract_material_type(title):
    title_lower = str(title).lower()

    if any(word in title_lower for word in ["denim", "jeans"]):
        return "Denim"
    elif any(word in title_lower for word in ["knit", "knitted"]):
        return "Knit"
    elif any(word in title_lower for word in ["cotton"]):
        return "Cotton"
    elif any(word in title_lower for word in ["linen"]):
        return "Linen"
    elif any(word in title_lower for word in ["wool"]):
        return "Wool"
    elif any(word in title_lower for word in ["polyester"]):
        return "Polyester"
    elif any(word in title_lower for word in ["silk"]):
        return "Silk"
    else:
        return "Cotton Blend"


df["material_type"] = df["title"].apply(extract_material_type)

# 7. Fit Type
print("Extracting fit types...")


def extract_fit_type(title):
    title_lower = str(title).lower()

    if "slim fit" in title_lower:
        return "Slim"
    elif "regular fit" in title_lower:
        return "Regular"
    elif "relax fit" in title_lower or "loose fit" in title_lower:
        return "Relaxed"
    elif "straight" in title_lower:
        return "Straight"
    elif "carrot" in title_lower:
        return "Carrot"
    elif "bootcut" in title_lower:
        return "Bootcut"
    elif "skinny" in title_lower:
        return "Skinny"
    else:
        return "Regular"


df["fit_type"] = df["title"].apply(extract_fit_type)

# 8. Size Variant
print("Extracting size variants...")


def extract_size_variant(variant):
    if pd.isna(variant):
        return "Not Specified"

    variant_str = str(variant)

    # Size patterns
    size_patterns = [
        r"/([SMLX]+)\s*$",  # S, M, L, XL, etc.
        r"/(\d+-\d+\s*[MY])",  # 6-9 M, 2 Y, etc.
        r"/(S-\d+)",  # S-30, S-32, etc.
        r"/(\d+)",  # 30, 32, etc.
        r"/(Free Size)",
        r"/(Mix)",
        r"/(One Size)",
    ]

    for pattern in size_patterns:
        match = re.search(pattern, variant_str)
        if match:
            return match.group(1).strip()

    return "Free Size"


df["size_variant"] = df["variant"].apply(extract_size_variant)

# 9. Style Type
print("Extracting style types...")


def extract_style_type(title):
    title_lower = str(title).lower()

    if any(word in title_lower for word in ["casual", "everyday"]):
        return "Casual"
    elif any(word in title_lower for word in ["formal", "suit", "dress", "office"]):
        return "Formal"
    elif any(word in title_lower for word in ["sport", "active", "gym", "athletic"]):
        return "Sports"
    elif any(word in title_lower for word in ["basic", "plain"]):
        return "Basic"
    elif any(
        word in title_lower for word in ["graphic", "print", "typography", "embroidery"]
    ):
        return "Graphic"
    elif any(word in title_lower for word in ["vintage", "retro"]):
        return "Vintage"
    else:
        return "Casual"


df["style_type"] = df["title"].apply(extract_style_type)

# 10. Create Price Tiers
print("Creating price tiers...")


def get_price_tier(price):
    if pd.isna(price) or price == 0:
        return "Unknown"
    elif price < 500:
        return "Budget (<500)"
    elif price < 1000:
        return "Economy (500-1k)"
    elif price < 1500:
        return "Mid-Range (1k-1.5k)"
    elif price < 2000:
        return "Premium (1.5k-2k)"
    elif price < 3000:
        return "Luxury (2k-3k)"
    else:
        return "Premium Luxury (3k+)"


df["price_tier"] = df["price_clean"].apply(get_price_tier)

# 11. Create Discount Levels
print("Creating discount levels...")


def get_discount_level(discount):
    if pd.isna(discount) or discount == 0:
        return "No Discount"
    elif discount <= 0.2:
        return "Low (0-20%)"
    elif discount <= 0.4:
        return "Medium (21-40%)"
    elif discount <= 0.6:
        return "High (41-60%)"
    else:
        return "Massive (61%+)"


df["discount_level"] = df["discount_clean"].apply(get_discount_level)

# 12. Handle Missing Values and Create Additional Columns
print("Handling missing values and creating additional columns...")
df["variant"] = df["variant"].fillna("Not Specified")
df["has_image"] = ~df["image_url"].isna() & (df["image_url"] != "")
df["availability"] = True  # Assuming all products are available

# 13. Calculate Savings and Value
print("Calculating savings...")
df["savings"] = df["original_price_clean"] - df["price_clean"]
df["savings_percentage"] = (df["savings"] / df["original_price_clean"]).fillna(0)

# 14. Simple Features
print("Creating simple features...")
df["title_length"] = df["title"].str.len()
df["is_discounted"] = df["discount_clean"] > 0

# 15. Select and reorder columns as requested
print("Selecting and reordering columns...")
final_columns = [
    "product_id",
    "title",
    "brand",
    "category",
    "product_url",
    "image_url",
    "price_clean",
    "original_price_clean",
    "sale_price_clean",
    "discount_clean",
    "is_discounted",
    "price_tier",
    "savings",
    "savings_percentage",
    "discount_level",
    "product_type",
    "primary_color",
    "material_type",
    "fit_type",
    "size_variant",
    "style_type",
    "title_length",
    "has_image",
    "availability",
]

# Create final dataframe with only the requested columns
final_df = df[final_columns].copy()

# Check for any remaining price conversion issues
print("Checking for price conversion issues...")
price_issues = final_df[final_df["price_clean"].isna()]
if len(price_issues) > 0:
    print(f"Found {len(price_issues)} products with price conversion issues:")
    print(price_issues[["title", "price_clean"]].head())
else:
    print("All prices converted successfully!")

# Results
print("=" * 50)
print("ENGINE DATA PROCESSING COMPLETED!")
print("=" * 50)
print(f"Original shape: {df.shape}")
print(f"Final shape: {final_df.shape}")
print(f"Columns in final dataset: {len(final_columns)}")

# Show sample results
print("\nSample Results:")
print(final_df.head(10))

# Basic stats
print("\nBasic Statistics:")
print(f"Average Price: PKR {final_df['price_clean'].mean():.2f}")
print(f"Total Products: {len(final_df)}")
print(
    f"Discounted Products: {final_df['is_discounted'].sum()} ({final_df['is_discounted'].mean()*100:.1f}%)"
)
print(f"Product Types: {final_df['product_type'].nunique()} types")

# Save cleaned data
print("\nSaving cleaned data...")
final_df.to_csv("../cleaned/engine.csv", index=False)
print("Cleaned data saved as '../cleaned/engine.csv'")

# Quick analysis
print("\nQuick Analysis:")
print("Product Type Distribution:")
print(final_df["product_type"].value_counts())

print("\nColor Distribution:")
print(final_df["primary_color"].value_counts().head(10))

print("\nMaterial Type Distribution:")
print(final_df["material_type"].value_counts())

print("\nFit Type Distribution:")
print(final_df["fit_type"].value_counts())

print("\nStyle Type Distribution:")
print(final_df["style_type"].value_counts())

print("\nPrice Tier Distribution:")
print(final_df["price_tier"].value_counts())

print("\nDiscount Level Distribution:")
print(final_df["discount_level"].value_counts())

print("\nSize Variant Distribution:")
print(final_df["size_variant"].value_counts().head(10))
