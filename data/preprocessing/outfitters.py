import pandas as pd
import numpy as np

# Load the data
print("Loading Outfitters data...")
df = pd.read_csv("../old/outfitters.csv")
print(f"Original data: {df.shape}")

# Display unique price values to see what we're dealing with
print("\nSample price values:")
print(df["price"].unique()[:10])

# 1. Clean Price Columns
print("\nCleaning prices...")


def clean_price_value(price_str):
    if pd.isna(price_str):
        return np.nan
    # Convert to string and remove PKR, commas, and percentage info
    price_str = str(price_str)
    # Remove PKR and any currency symbols
    price_str = (
        price_str.replace("PKR", "")
        .replace("Rs.", "")
        .replace("Rs", "")
        .replace("₹", "")
        .replace("$", "")
        .replace("From", "")
    )
    # Remove percentage info like "-0%"
    price_str = price_str.split("-")[0].strip()
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
    if pd.isna(discount) or discount == "Sold out":
        return 0
    elif isinstance(discount, str) and "%" in discount:
        # Handle negative percentages like "-0%"
        discount_str = discount.replace("%", "").replace("-", "")
        if discount_str == "":
            return 0
        return float(discount_str) / 100
    else:
        return 0


df["discount_clean"] = df["discount"].apply(clean_discount)

# 3. Product Type Categorization
print("Categorizing products...")


def get_product_type(title):
    title_lower = str(title).lower()
    if any(word in title_lower for word in ["pants", "trousers"]):
        return "Pants"
    elif "jeans" in title_lower:
        return "Jeans"
    elif "shorts" in title_lower:
        return "Shorts"
    elif (
        any(word in title_lower for word in ["polo", "shirt"])
        and "t-shirt" not in title_lower
    ):
        return "Shirts"
    elif (
        "t-shirt" in title_lower or "tshirt" in title_lower or "t shirt" in title_lower
    ):
        return "T-Shirts"
    elif "sweatshirt" in title_lower:
        return "Sweatshirts"
    elif "pull" in title_lower and "over" in title_lower:
        return "Pullovers"
    elif "tank" in title_lower or "camisole" in title_lower:
        return "Tank Tops"
    elif "hoodie" in title_lower:
        return "Hoodies"
    elif "sweater" in title_lower:
        return "Sweaters"
    elif "jacket" in title_lower:
        return "Jackets"
    elif "dress" in title_lower:
        return "Dresses"
    elif "skirt" in title_lower:
        return "Skirts"
    elif "socks" in title_lower:
        return "Socks"
    elif "mist" in title_lower:
        return "Fragrances"
    else:
        return "Other"


df["product_type"] = df["title"].apply(get_product_type)

# 4. Extract Primary Color (Simplified - would need more sophisticated analysis)
print("Extracting primary colors...")


def get_primary_color(title):
    title_lower = str(title).lower()
    colors = [
        "black",
        "white",
        "blue",
        "red",
        "green",
        "yellow",
        "pink",
        "purple",
        "orange",
        "brown",
        "gray",
        "grey",
        "navy",
        "beige",
        "cream",
        "khaki",
    ]
    for color in colors:
        if color in title_lower:
            return color.title()
    return "Multi/Unknown"


df["primary_color"] = df["title"].apply(get_primary_color)

# 5. Extract Fit Type
print("Extracting fit types...")


def get_fit_type(title):
    title_lower = str(title).lower()
    if "relaxed" in title_lower:
        return "Relaxed"
    elif "slim" in title_lower:
        return "Slim"
    elif "straight" in title_lower:
        return "Straight"
    elif "skinny" in title_lower:
        return "Skinny"
    elif "baggy" in title_lower:
        return "Baggy"
    elif "loose" in title_lower:
        return "Loose"
    elif "cropped" in title_lower:
        return "Cropped"
    elif "varsity" in title_lower:
        return "Varsity"
    elif "wide" in title_lower or "flared" in title_lower:
        return "Wide"
    elif "balloon" in title_lower or "barrel" in title_lower:
        return "Oversized"
    else:
        return "Regular"


df["fit_type"] = df["title"].apply(get_fit_type)

# 6. Extract Fabric/Material
print("Extracting materials...")


def get_material_type(title):
    title_lower = str(title).lower()
    if "mesh" in title_lower:
        return "Mesh"
    elif "ribbed" in title_lower:
        return "Ribbed"
    elif "linen" in title_lower:
        return "Linen"
    elif "denim" in title_lower:
        return "Denim"
    elif "leather" in title_lower:
        return "Leather"
    elif "knit" in title_lower:
        return "Knit"
    elif "faux" in title_lower:
        return "Faux Leather"
    elif "cotton" in title_lower:
        return "Cotton"
    elif "graphic" in title_lower or "slogan" in title_lower:
        return "Printed Cotton"
    elif "striped" in title_lower:
        return "Striped Cotton"
    elif "basic" in title_lower:
        return "Basic Cotton"
    else:
        return "Cotton Blend"


df["material_type"] = df["title"].apply(get_material_type)

# 7. Extract Product Style
print("Extracting styles...")


def get_product_style(title):
    title_lower = str(title).lower()
    if "crew neck" in title_lower:
        return "Crew Neck"
    elif "mock neck" in title_lower:
        return "Mock Neck"
    elif "v-neck" in title_lower or "v neck" in title_lower:
        return "V-Neck"
    elif "varsity" in title_lower:
        return "Varsity"
    elif "slogan" in title_lower:
        return "Slogan Print"
    elif "graphic" in title_lower:
        return "Graphic Print"
    elif "striped" in title_lower:
        return "Striped"
    elif "embroidered" in title_lower:
        return "Embroidered"
    elif "checkered" in title_lower:
        return "Checkered"
    elif "basic" in title_lower:
        return "Basic"
    elif "cropped" in title_lower:
        return "Cropped"
    elif "color block" in title_lower or "color-block" in title_lower:
        return "Color Block"
    else:
        return "Basic"


df["style_type"] = df["title"].apply(get_product_style)

# 8. Create Price Tiers
print("Creating price tiers...")


def get_price_tier(price):
    if pd.isna(price) or price == 0:
        return "Unknown"
    elif price < 2000:
        return "Budget (<2k)"
    elif price < 3000:
        return "Economy (2k-3k)"
    elif price < 4000:
        return "Mid-Range (3k-4k)"
    elif price < 5000:
        return "Premium (4k-5k)"
    else:
        return "Luxury (5k+)"


df["price_tier"] = df["price_clean"].apply(get_price_tier)

# 9. Create Discount Levels
print("Creating discount levels...")


def get_discount_level(discount):
    if pd.isna(discount) or discount == 0:
        return "No Discount"
    elif discount < 0.1:
        return "Small Discount (<10%)"
    elif discount < 0.3:
        return "Medium Discount (10-30%)"
    elif discount < 0.5:
        return "Large Discount (30-50%)"
    else:
        return "Major Discount (50%+)"


df["discount_level"] = df["discount_clean"].apply(get_discount_level)

# 10. Handle Missing Values and Create Additional Features
print("Handling missing values and creating features...")
df["variant"] = df["variant"].fillna("Not Specified")
df["has_image"] = ~df["image_url"].isna() & (df["image_url"] != "N/A")

# 11. Calculate Savings and Value
print("Calculating savings...")
df["savings"] = df["original_price_clean"] - df["sale_price_clean"]
df["savings_percentage"] = (df["savings"] / df["original_price_clean"] * 100).fillna(0)

# 12. Extract Size Variant Information
print("Extracting size variant information...")


def extract_size_variant(variant):
    if pd.isna(variant):
        return "Not Specified"
    variant_str = str(variant).lower()

    # Extract size ranges
    if "sizes:" in variant_str:
        size_info = variant_str.split("sizes:")[-1].strip()
        return size_info.title()
    elif "size" in variant_str:
        return "Standard Sizes"
    else:
        return variant_str.title()


df["size_variant"] = df["variant"].apply(extract_size_variant)

# 13. Create Availability Status
print("Creating availability status...")


def get_availability(variant):
    if pd.isna(variant):
        return "Unknown"
    variant_str = str(variant).lower()
    if "sold out" in variant_str:
        return "Out of Stock"
    else:
        return "In Stock"


df["availability"] = df["variant"].apply(get_availability)

# 14. Simple Features
print("Creating simple features...")
df["title_length"] = df["title"].str.len()
df["is_discounted"] = df["discount_clean"] > 0
df["product_id"] = df["product_url"].str.extract(r"products/([^/?]+)")

# Check for any remaining price conversion issues
print("\nChecking for price conversion issues...")
price_issues = df[df["price_clean"].isna()]
if len(price_issues) > 0:
    print(f"Found {len(price_issues)} products with price conversion issues:")
    print(price_issues[["title", "price"]].head())
else:
    print("All prices converted successfully!")

# Create final dataframe with requested columns
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

# Ensure all columns exist
for col in final_columns:
    if col not in df.columns:
        df[col] = None  # Add missing columns

# Select only the requested columns
df_final = df[final_columns].copy()

# Results
print("\n" + "=" * 50)
print("OUTFITTERS DATA PROCESSING COMPLETED!")
print("=" * 50)
print(f"Original shape: {df.shape}")
print(f"Final shape: {df_final.shape}")
print(f"Columns in final dataset: {len(df_final.columns)}")

# Show sample results
print("\nSample Results:")
print(df_final.head(10))

# Basic stats
print("\nBasic Statistics:")
print(f"Average Price: PKR {df_final['price_clean'].mean():.2f}")
print(f"Total Products: {len(df_final)}")
print(
    f"Discounted Products: {df_final['is_discounted'].sum()} ({df_final['is_discounted'].mean()*100:.1f}%)"
)
print(f"Product Types: {df_final['product_type'].nunique()} types")
print(f"Availability - In Stock: {(df_final['availability'] == 'In Stock').sum()}")

# Save cleaned data
print("\nSaving cleaned data...")
df_final.to_csv("../cleaned/outfitters.csv", index=False)
print("Cleaned data saved as 'outfitters.csv'")

# Quick analysis
print("\nQuick Analysis:")
print("\nProduct Type Distribution:")
print(df_final["product_type"].value_counts())

print("\nFit Type Distribution:")
print(df_final["fit_type"].value_counts())

print("\nPrice Tier Distribution:")
print(df_final["price_tier"].value_counts())

print("\nMaterial Type Distribution:")
print(df_final["material_type"].value_counts())

print("\nStyle Type Distribution:")
print(df_final["style_type"].value_counts())

print("\nAvailability Summary:")
print(df_final["availability"].value_counts())

print("\nPrimary Color Summary:")
print(df_final["primary_color"].value_counts().head(10))

print("\nDiscount Level Summary:")
print(df_final["discount_level"].value_counts())
