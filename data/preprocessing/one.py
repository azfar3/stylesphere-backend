import pandas as pd
import numpy as np

# Load the data
print("Loading One brand data...")
df = pd.read_csv("../old/one.csv")
print(f"Original data: {df.shape}")

# 1. Clean Price Columns
print("Cleaning prices...")


def clean_price_value(price_str):
    if pd.isna(price_str):
        return np.nan
    # Convert to string and remove Rs, commas, and any other characters
    price_str = str(price_str)
    # Remove Rs and any currency symbols
    price_str = (
        price_str.replace("Rs.", "")
        .replace("Rs", "")
        .replace("₹", "")
        .replace("$", "")
        .replace("PKR", "")
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
print("Cleaning discount information...")


def extract_discount_info(discount_str):
    if pd.isna(discount_str):
        return 0

    discount_str = str(discount_str)

    # Extract the installment amount for discount calculation
    if "Pay" in discount_str and "now" in discount_str:
        try:
            # Extract the installment amount
            installment_amount = "".join(
                char
                for char in discount_str.split("Pay")[1].split("now")[0]
                if char.isdigit() or char == "."
            )
            if installment_amount:
                installment_amount = float(installment_amount)
                # Calculate the discount percentage based on installment
                price = (
                    df.loc[df["discount"] == discount_str, "price_clean"].iloc[0]
                    if discount_str in df["discount"].values
                    else 0
                )
                if price > 0:
                    discount_pct = (price - installment_amount) / price
                    return discount_pct
        except:
            pass

    return 0


df["discount_clean"] = df["discount"].apply(extract_discount_info)

# 3. Product Type Categorization
print("Categorizing products...")


def get_product_type(title):
    title_lower = str(title).lower()
    if "sweater" in title_lower:
        return "Sweaters"
    elif "hoodie" in title_lower:
        return "Hoodies"
    elif "blazer" in title_lower or "coat" in title_lower:
        return "Outerwear"
    elif "shirt" in title_lower:
        return "Shirts"
    elif any(word in title_lower for word in ["sweatshirt", "pullover"]):
        return "Sweatshirts"
    elif any(word in title_lower for word in ["pants", "trousers"]):
        return "Bottoms"
    elif any(word in title_lower for word in ["tee", "t-shirt"]):
        return "T-Shirts"
    elif "jacket" in title_lower:
        return "Jackets"
    elif "jeans" in title_lower:
        return "Jeans"
    elif "short" in title_lower:
        return "Shorts"
    elif "dress" in title_lower:
        return "Dresses"
    elif "boot" in title_lower or "shoe" in title_lower:
        return "Footwear"
    elif "belt" in title_lower:
        return "Accessories"
    else:
        return "Other"


df["product_type"] = df["title"].apply(get_product_type)

# 4. Extract Material Type
print("Extracting material type...")


def extract_material_type(title):
    title_lower = str(title).lower()
    if any(word in title_lower for word in ["denim", "jeans"]):
        return "Denim"
    elif any(word in title_lower for word in ["cotton"]):
        return "Cotton"
    elif any(word in title_lower for word in ["linen"]):
        return "Linen"
    elif any(word in title_lower for word in ["wool", "sweater"]):
        return "Wool"
    elif any(word in title_lower for word in ["leather"]):
        return "Leather"
    elif any(word in title_lower for word in ["silk"]):
        return "Silk"
    elif any(word in title_lower for word in ["faux fur", "fur"]):
        return "Faux Fur"
    elif any(word in title_lower for word in ["knit", "knitted"]):
        return "Knit"
    else:
        return "Mixed/Unknown"


df["material_type"] = df["title"].apply(extract_material_type)

# 5. Extract Fit Type
print("Extracting fit type...")


def extract_fit_type(title):
    title_lower = str(title).lower()
    if "slim" in title_lower:
        return "Slim"
    elif "baggy" in title_lower or "loose" in title_lower:
        return "Baggy"
    elif "skinny" in title_lower:
        return "Skinny"
    elif "regular" in title_lower:
        return "Regular"
    elif "relax" in title_lower:
        return "Relaxed"
    elif "tapered" in title_lower:
        return "Tapered"
    elif "straight" in title_lower:
        return "Straight"
    else:
        return "Regular"


df["fit_type"] = df["title"].apply(extract_fit_type)

# 6. Extract Size Variant
print("Extracting size variant...")


def extract_size_variant(title):
    title_lower = str(title).lower()
    if "cropped" in title_lower or "crop" in title_lower:
        return "Cropped"
    elif "oversized" in title_lower or "over-sized" in title_lower:
        return "Oversized"
    elif "wide leg" in title_lower or "wide-leg" in title_lower:
        return "Wide Leg"
    elif "high waist" in title_lower or "high-waist" in title_lower:
        return "High Waist"
    elif "long" in title_lower and "coat" in title_lower:
        return "Long"
    elif "short" in title_lower and not any(
        word in title_lower for word in ["short sleeve", "shorts"]
    ):
        return "Short"
    else:
        return "Standard"


df["size_variant"] = df["title"].apply(extract_size_variant)

# 7. Extract Style Type
print("Extracting style type...")


def extract_style_type(title):
    title_lower = str(title).lower()
    if any(word in title_lower for word in ["casual"]):
        return "Casual"
    elif any(
        word in title_lower for word in ["formal", "office", "business", "blazer"]
    ):
        return "Formal"
    elif any(word in title_lower for word in ["sports", "sport", "gym", "athletic"]):
        return "Sports"
    elif any(word in title_lower for word in ["vintage", "retro"]):
        return "Vintage"
    elif any(word in title_lower for word in ["street", "urban", "hip hop"]):
        return "Streetwear"
    elif any(word in title_lower for word in ["designer", "luxury", "premium"]):
        return "Designer"
    else:
        return "Casual"


df["style_type"] = df["title"].apply(extract_style_type)

# 8. Extract Color from Product ID and Variant
print("Extracting colors...")


def extract_color_from_id(product_id):
    if pd.isna(product_id):
        return "Unknown"

    product_str = str(product_id).upper()
    color_mapping = {
        "BLK": "Black",
        "BLU": "Blue",
        "NVY": "Navy",
        "GRY": "Grey",
        "WHT": "White",
        "BKW": "Black White",
        "BNY": "Black Navy",
        "DKO": "Dark Olive",
        "BGY": "Beige Grey",
        "DGR": "Dark Green",
        "BGE": "Beige",
        "BRN": "Brown",
        "OWH": "Off White",
        "KHK": "Khaki",
        "RED": "Red",
        "PNK": "Pink",
        "GRN": "Green",
        "YLW": "Yellow",
        "ORG": "Orange",
        "PRP": "Purple",
        "MRN": "Maroon",
        "TEL": "Teal",
        "BLW": "Blue White",
        "OLV": "Olive",
        "LTG": "Light Grey",
        "DKG": "Dark Grey",
    }

    for color_code, color_name in color_mapping.items():
        if color_code in product_str:
            return color_name

    return "Unknown"


df["primary_color"] = df["variant"].apply(extract_color_from_id)

# 9. Create Price Tiers
print("Creating price tiers...")


def get_price_tier(price):
    if pd.isna(price) or price == 0:
        return "Unknown"
    elif price < 3000:
        return "Budget (<3k)"
    elif price < 6000:
        return "Economy (3k-6k)"
    elif price < 10000:
        return "Mid-Range (6k-10k)"
    elif price < 15000:
        return "Premium (10k-15k)"
    else:
        return "Luxury (15k+)"


df["price_tier"] = df["price_clean"].apply(get_price_tier)

# 10. Create Discount Levels
print("Creating discount levels...")


def get_discount_level(discount):
    if pd.isna(discount) or discount == 0:
        return "No Discount"
    elif discount <= 0.2:
        return "Low Discount"
    elif discount <= 0.4:
        return "Medium Discount"
    else:
        return "High Discount"


df["discount_level"] = df["discount_clean"].apply(get_discount_level)

# 11. Handle Missing Values and Create Additional Columns
print("Handling missing values...")
df["variant"] = df["variant"].fillna("Not Specified")
df["has_image"] = ~df["image_url"].isna() & (df["image_url"] != "N/A")

# 12. Calculate Savings and Value
print("Calculating savings...")
df["savings"] = df["original_price_clean"] - df["sale_price_clean"]
df["savings_percentage"] = (df["savings"] / df["original_price_clean"]).fillna(0)

# 13. Simple Features
print("Creating simple features...")
df["title_length"] = df["title"].str.len()
df["is_discounted"] = df["discount_clean"] > 0

# Fix product_id scientific notation
df["product_id_clean"] = df["product_id"].apply(
    lambda x: str(int(float(x))) if pd.notna(x) and "E+" in str(x) else str(x)
)

# 14. Create Final DataFrame with Exact Columns Requested
print("Creating final dataframe with requested columns...")

final_columns = [
    "product_id_clean",
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

# Create final dataframe
final_df = df[final_columns].copy()

# Rename product_id_clean to product_id for final output
final_df = final_df.rename(columns={"product_id_clean": "product_id"})

# Results
print("=" * 50)
print("ONE BRAND DATA PROCESSING COMPLETED!")
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

# Save cleaned data
print("\nSaving cleaned data...")
final_df.to_csv("../cleaned/one.csv", index=False)
print("Cleaned data saved as '../cleaned/one.csv'")

# Quick analysis
print("\nQuick Analysis:")
print("Product Type Distribution:")
print(final_df["product_type"].value_counts())

print("\nPrice Tier Distribution:")
print(final_df["price_tier"].value_counts())

print("\nMaterial Type Distribution:")
print(final_df["material_type"].value_counts())

print("\nFit Type Distribution:")
print(final_df["fit_type"].value_counts())

print("\nStyle Type Distribution:")
print(final_df["style_type"].value_counts())

print("\nColor Distribution:")
print(final_df["primary_color"].value_counts().head(10))

print("\nDiscount Level Distribution:")
print(final_df["discount_level"].value_counts())

print("\nAvailability Distribution:")
print(final_df["availability"].value_counts())

print(f"\nFinal columns: {list(final_df.columns)}")
