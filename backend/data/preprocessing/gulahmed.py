import pandas as pd
import numpy as np

# Load the data
print("Loading data...")
df = pd.read_csv("../old/gulahmed.csv")
print(f"Original data: {df.shape}")

# 1. Extract Product ID from URL
print("Extracting product IDs...")
def extract_product_id(url):
    if pd.isna(url):
        return None
    try:
        return url.split('/products/')[-1].split('?')[0]
    except:
        return None

df['product_id'] = df['product_url'].apply(extract_product_id)

# 2. Clean Price Columns
print("Cleaning prices...")
for col in ["price", "original_price", "sale_price"]:
    df[f"{col}_clean"] = (
        df[col]
        .str.replace("fromRs.", "", regex=False)
        .str.replace("Rs.", "", regex=False)
        .str.replace(",", "")
        .str.replace("Rs", "")
        .str.strip()
        .replace("", np.nan)
        .astype(float)
    )

# Fill missing original prices with sale prices
df["original_price_clean"] = df["original_price_clean"].fillna(df["sale_price_clean"])

# 3. Clean Discount Column
print("Cleaning discounts...")
df["discount_clean"] = (
    df["discount"]
    .str.replace("%", "")
    .str.replace("-", "")
    .replace("", "0")
    .astype(float)
    / 100
)

# 4. Calculate additional discount metrics
df["is_discounted"] = df["discount_clean"] > 0
df["savings"] = df["original_price_clean"] - df["sale_price_clean"]
df["savings_percentage"] = (df["savings"] / df["original_price_clean"] * 100).fillna(0)

# 5. Product Type Categorization
print("Categorizing products...")
def get_product_type(title):
    title_lower = str(title).lower()
    if "unstitched" in title_lower:
        return "Unstitched Fabric"
    elif any(word in title_lower for word in ["suit", "shalwar kameez"]):
        return "Suit"
    elif "kurta" in title_lower:
        return "Kurta"
    elif any(word in title_lower for word in ["shalwar", "pajama"]):
        return "Bottom Wear"
    elif any(word in title_lower for word in ["waistcoat", "waist coat"]):
        return "Waistcoat"
    elif any(word in title_lower for word in ["trouser", "jeans"]):
        return "Trousers"
    elif "shirt" in title_lower:
        return "Shirt"
    else:
        return "Other"

df["product_type"] = df["title"].apply(get_product_type)

# 6. Extract Material/Fabric Type
print("Extracting material types...")
def get_material_type(title):
    title_lower = str(title).lower()
    if "cotton" in title_lower and "blended" in title_lower:
        return "Cotton Blended"
    elif "cotton" in title_lower:
        return "Cotton"
    elif "blended" in title_lower:
        return "Blended"
    elif "silk" in title_lower:
        return "Silk"
    elif "lawn" in title_lower:
        return "Lawn"
    elif "khaddar" in title_lower:
        return "Khaddar"
    elif "linen" in title_lower:
        return "Linen"
    else:
        return "Unknown"

df["material_type"] = df["title"].apply(get_material_type)

# 7. Extract Primary Color
print("Extracting colors...")
def get_primary_color(variant):
    if pd.isna(variant) or variant == "Default Title":
        return "Not Specified"

    variant_lower = str(variant).lower()
    colors = {
        "white": "White",
        "black": "Black",
        "blue": "Blue",
        "navy": "Navy Blue",
        "red": "Red",
        "green": "Green",
        "grey": "Grey",
        "gray": "Grey",
        "brown": "Brown",
        "cream": "Cream",
        "beige": "Beige",
        "purple": "Purple",
        "maroon": "Maroon",
        "pink": "Pink",
        "yellow": "Yellow",
        "orange": "Orange",
        "off white": "Off White",
        "sky blue": "Sky Blue",
        "royal blue": "Royal Blue",
        "dark grey": "Dark Grey",
        "light grey": "Light Grey",
        "charcoal": "Charcoal",
        "khaki": "Khaki"
    }

    for color_key, color_value in colors.items():
        if color_key in variant_lower:
            return color_value

    return "Multi-Color"

df["primary_color"] = df["variant"].apply(get_primary_color)

# 8. Extract Fit Type
print("Extracting fit types...")
def get_fit_type(title):
    title_lower = str(title).lower()
    if "regular fit" in title_lower:
        return "Regular Fit"
    elif "slim fit" in title_lower:
        return "Slim Fit"
    elif "skinny" in title_lower:
        return "Skinny Fit"
    elif "loose" in title_lower:
        return "Loose Fit"
    elif "comfort" in title_lower:
        return "Comfort Fit"
    else:
        return "Not Specified"

df["fit_type"] = df["title"].apply(get_fit_type)

# 9. Extract Style Type
print("Extracting style types...")
def get_style_type(title):
    title_lower = str(title).lower()
    if "embroidered" in title_lower:
        return "Embroidered"
    elif "printed" in title_lower:
        return "Printed"
    elif "plain" in title_lower or "basic" in title_lower:
        return "Plain/Basic"
    elif "designer" in title_lower:
        return "Designer"
    elif "formal" in title_lower:
        return "Formal"
    elif "casual" in title_lower:
        return "Casual"
    else:
        return "Not Specified"

df["style_type"] = df["title"].apply(get_style_type)

# 10. Create Price Tiers
print("Creating price tiers...")
def get_price_tier(price):
    if pd.isna(price) or price == 0:
        return "Unknown"
    elif price < 1000:
        return "Budget (<1k)"
    elif price < 3000:
        return "Economy (1k-3k)"
    elif price < 7000:
        return "Mid-Range (3k-7k)"
    elif price < 15000:
        return "Premium (7k-15k)"
    else:
        return "Luxury (15k+)"

df["price_tier"] = df["sale_price_clean"].apply(get_price_tier)

# 11. Create Discount Levels
print("Creating discount levels...")
def get_discount_level(discount):
    if pd.isna(discount) or discount == 0:
        return "No Discount"
    elif discount <= 0.3:
        return "Low Discount (0-30%)"
    elif discount <= 0.5:
        return "Medium Discount (31-50%)"
    else:
        return "High Discount (51%+)"

df["discount_level"] = df["discount_clean"].apply(get_discount_level)

# 12. Handle Missing Values and create additional features
print("Handling missing values...")
df["variant"] = df["variant"].fillna("Not Specified")
df["size_variant"] = df["variant"]  # Using variant as size_variant
df["has_image"] = ~df["image_url"].isna() & (df["image_url"] != "N/A")
df["title_length"] = df["title"].str.len()
df["availability"] = "In Stock"  # Assuming all are available unless specified otherwise

# 13. Select and reorder final columns
final_columns = [
    'product_id', 'title', 'brand', 'category', 'product_url', 'image_url',
    'price_clean', 'original_price_clean', 'sale_price_clean', 'discount_clean',
    'is_discounted', 'price_tier', 'savings', 'savings_percentage', 'discount_level',
    'product_type', 'primary_color', 'material_type', 'fit_type', 'size_variant', 'style_type',
    'title_length', 'has_image', 'availability'
]

# Create final dataframe with only the required columns
final_df = df[final_columns]

# Results
print("\n" + "=" * 50)
print("PROCESSING COMPLETED!")
print("=" * 50)
print(f"Original shape: {df.shape}")
print(f"Final shape: {final_df.shape}")
print(f"Columns created: {len(final_columns)}")

# Show sample results
print("\nSample Results:")
print(final_df.head(10))

# Basic stats
print("\nBasic Statistics:")
print(f"Average Price: Rs. {final_df['sale_price_clean'].mean():.2f}")
print(f"Average Discount: {final_df['discount_clean'].mean()*100:.1f}%")
print(f"Total Products: {len(final_df)}")
print(f"Discounted Products: {final_df['is_discounted'].sum()} ({final_df['is_discounted'].mean()*100:.1f}%)")

# Quick analysis
print("\nPrice Tier Distribution:")
print(final_df["price_tier"].value_counts())

print("\nDiscount Level Distribution:")
print(final_df["discount_level"].value_counts())

print("\nProduct Type Distribution:")
print(final_df["product_type"].value_counts().head(10))

print("\nMaterial Type Distribution:")
print(final_df["material_type"].value_counts().head())

# Save cleaned data
print("\nSaving cleaned data...")
final_df.to_csv("../cleaned/gulahmed.csv", index=False)
print("Cleaned data saved as 'gulahmed.csv'")