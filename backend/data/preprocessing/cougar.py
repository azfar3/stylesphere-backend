import pandas as pd
import numpy as np

# Load the data
print("Loading Cougar data...")
df = pd.read_csv("../old/cougar.csv")
print(f"Original data: {df.shape}")

# Display unique price values to see what we're dealing with
print("\nSample price values:")
print(df["price"].unique()[:10])

# 1. Clean Price Columns
print("\nCleaning prices...")


def clean_price_value(price_str):
    if pd.isna(price_str):
        return np.nan
    # Convert to string and remove Rs, commas, and any other characters
    price_str = str(price_str)
    # Remove Rs and any currency symbols
    price_str = (
        price_str.replace("Rs.", "").replace("Rs", "").replace("₹", "").replace("$", "")
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

# 2. Clean Discount Column
print("Cleaning discounts...")


def clean_discount(discount):
    if pd.isna(discount) or discount == "Sold out":
        return 0
    elif isinstance(discount, str) and "%" in discount:
        return float(discount.replace("%", "").replace("-", "")) / 100
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
    elif any(word in title_lower for word in ["polo", "shirt"]):
        return "Shirts"
    elif "t-shirt" in title_lower:
        return "T-Shirts"
    elif "dress" in title_lower:
        return "Dresses"
    elif "jacket" in title_lower or "hoodie" in title_lower or "sweater" in title_lower:
        return "Outerwear"
    elif "top" in title_lower:
        return "Tops"
    else:
        return "Other"


df["product_type"] = df["title"].apply(get_product_type)

# 4. Extract Fit Type
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
    elif "skater" in title_lower:
        return "Skater"
    elif "boot cut" in title_lower:
        return "Boot Cut"
    elif "wide leg" in title_lower:
        return "Wide Leg"
    elif "tapered" in title_lower:
        return "Tapered"
    elif "oversized" in title_lower:
        return "Oversized"
    elif "jogger" in title_lower:
        return "Jogger"
    else:
        return "Regular"


df["fit_type"] = df["title"].apply(get_fit_type)

# 5. Extract Fabric/Material
print("Extracting materials...")


def get_material_type(title):
    title_lower = str(title).lower()
    if "chino" in title_lower:
        return "Chino"
    elif "denim" in title_lower:
        return "Denim"
    elif "knit" in title_lower:
        return "Knit"
    elif "muslin" in title_lower:
        return "Muslin"
    elif "activewear" in title_lower:
        return "Activewear"
    elif "textured" in title_lower:
        return "Textured"
    elif "pique" in title_lower:
        return "Pique"
    elif "interlock" in title_lower:
        return "Interlock"
    elif "ottoman" in title_lower:
        return "Ottoman"
    elif "linen" in title_lower:
        return "Linen"
    elif "cotton" in title_lower:
        return "Cotton"
    elif "silk" in title_lower:
        return "Silk"
    elif "viscose" in title_lower:
        return "Viscose"
    else:
        return "Mixed"


df["material_type"] = df["title"].apply(get_material_type)

# 6. Extract Primary Color
print("Extracting primary colors...")


def get_primary_color(title):
    title_lower = str(title).lower()
    colors = {
        "black": ["black", "blk"],
        "white": ["white", "wht"],
        "blue": ["blue", "navy", "nvy", "blu"],
        "red": ["red"],
        "green": ["green", "grn"],
        "pink": ["pink", "pnk"],
        "grey": ["grey", "gray", "gry"],
        "brown": ["brown", "brn"],
        "beige": ["beige", "bei"],
        "purple": ["purple", "prp"],
        "yellow": ["yellow", "ylw"],
        "orange": ["orange", "org"],
        "khaki": ["khaki", "khk"],
        "olive": ["olive", "olv"],
    }

    for color, keywords in colors.items():
        for keyword in keywords:
            if keyword in title_lower:
                return color.title()

    return "Multi-color"


df["primary_color"] = df["title"].apply(get_primary_color)

# 7. Extract Product Style
print("Extracting styles...")


def get_product_style(title):
    title_lower = str(title).lower()
    if "henley" in title_lower:
        return "Henley"
    elif "raglan" in title_lower:
        return "Raglan"
    elif "crew neck" in title_lower:
        return "Crew Neck"
    elif "johnny collar" in title_lower:
        return "Johnny Collar"
    elif "accent collar" in title_lower:
        return "Accent Collar"
    elif "tipped" in title_lower:
        return "Tipped"
    elif "printed" in title_lower:
        return "Printed"
    elif "cargo" in title_lower:
        return "Cargo"
    elif "5 pocket" in title_lower:
        return "5 Pocket"
    elif "graphic" in title_lower:
        return "Graphic"
    elif "embroidered" in title_lower:
        return "Embroidered"
    elif "striped" in title_lower:
        return "Striped"
    elif "check" in title_lower or "checkered" in title_lower:
        return "Check"
    elif "jacquard" in title_lower:
        return "Jacquard"
    else:
        return "Basic"


df["style_type"] = df["title"].apply(get_product_style)

# 8. Create Price Tiers
print("Creating price tiers...")


def get_price_tier(price):
    if pd.isna(price) or price == 0:
        return "Unknown"
    elif price < 1500:
        return "Budget (<1.5k)"
    elif price < 2500:
        return "Economy (1.5k-2.5k)"
    elif price < 3500:
        return "Mid-Range (2.5k-3.5k)"
    else:
        return "Premium (3.5k+)"


df["price_tier"] = df["price_clean"].apply(get_price_tier)

# 9. Create Discount Levels
print("Creating discount levels...")


def get_discount_level(discount):
    if pd.isna(discount) or discount == 0:
        return "No Discount"
    elif discount == 0.5:
        return "50% Off"
    elif discount > 0.4:
        return "High Discount (40%+)"
    elif discount > 0.3:
        return "Medium Discount (30-40%)"
    elif discount > 0.2:
        return "Low Discount (20-30%)"
    else:
        return "Small Discount (<20%)"


df["discount_level"] = df["discount_clean"].apply(get_discount_level)

# 10. Handle Size Variant
print("Handling size variants...")
df["size_variant"] = df["variant"].fillna("Not Specified")

# 11. Handle Availability
print("Setting availability...")
df["availability"] = df["discount"].apply(
    lambda x: "Sold Out" if str(x) == "Sold out" else "In Stock"
)

# 12. Calculate Savings and Value
print("Calculating savings...")
df["savings"] = df["original_price_clean"] - df["price_clean"]
df["savings_percentage"] = (df["savings"] / df["original_price_clean"] * 100).fillna(0)

# 13. Simple Features
print("Creating simple features...")
df["title_length"] = df["title"].str.len()
df["is_discounted"] = df["discount_clean"] > 0
df["has_image"] = ~df["image_url"].isna() & (df["image_url"] != "")

# 14. Extract Product ID
print("Extracting product IDs...")
df["product_id"] = df["product_url"].str.extract(r"products/([^/?]+)")

# Check for any remaining price conversion issues
print("\nChecking for price conversion issues...")
price_issues = df[df["price_clean"].isna()]
if len(price_issues) > 0:
    print(f"Found {len(price_issues)} products with price conversion issues:")
    print(price_issues[["title", "price"]].head())
else:
    print("All prices converted successfully!")

# Create final dataframe with only the requested columns
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
        print(f"Warning: Column '{col}' not found in dataframe")

final_df = df[final_columns].copy()

# Results
print("\n" + "=" * 50)
print("COUGAR DATA PROCESSING COMPLETED!")
print("=" * 50)
print(f"Original shape: {df.shape}")
print(f"Final shape: {final_df.shape}")
print(f"Columns in final dataset: {len(final_columns)}")

# Show sample results
print("\nSample Results:")
print(final_df.head(10))

# Basic stats
print("\nBasic Statistics:")
print(f"Average Price: Rs. {final_df['price_clean'].mean():.2f}")
print(f"Total Products: {len(final_df)}")
print(
    f"Discounted Products: {final_df['is_discounted'].sum()} ({final_df['is_discounted'].mean()*100:.1f}%)"
)
print(f"Product Types: {final_df['product_type'].nunique()} types")
print(f"Availability - In Stock: {(final_df['availability'] == 'In Stock').sum()}")
print(f"Availability - Sold Out: {(final_df['availability'] == 'Sold Out').sum()}")

# Quick analysis
print("\nQuick Analysis:")
print("\nProduct Type Distribution:")
print(final_df["product_type"].value_counts())

print("\nFit Type Distribution:")
print(final_df["fit_type"].value_counts())

print("\nPrice Tier Distribution:")
print(final_df["price_tier"].value_counts())

print("\nMaterial Type Distribution:")
print(final_df["material_type"].value_counts().head(10))

print("\nPrimary Color Distribution:")
print(final_df["primary_color"].value_counts().head(10))

print("\nDiscount Level Distribution:")
print(final_df["discount_level"].value_counts())

# Save cleaned data
print("\nSaving cleaned data...")
final_df.to_csv("../cleaned/cougar.csv", index=False)
print("Cleaned data saved as '../cleaned/cougar.csv'")

# Display final column information
print(f"\nFinal columns ({len(final_columns)}):")
for i, col in enumerate(final_columns, 1):
    print(f"{i:2d}. {col}")
