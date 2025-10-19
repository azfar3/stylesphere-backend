# data_preprocessor.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import warnings

warnings.filterwarnings("ignore")


class HolidayPreprocessor:
    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.holidays = self.get_holidays()

    def get_holidays(self):
        holidays = {
            "eid_ul_fitr": ["2026-03-21", "2026-03-22", "2026-03-23"],
            "eid_ul_azha": ["2026-05-27", "2026-05-28"],
            "ashura": ["2026-06-25", "2026-06-26"],
            "eid_milad_un_nabi": ["2026-08-25"],
            "kashmir_day": ["2026-02-05"],
            "pakistan_day": ["2026-03-23"],
            "labour_day": ["2026-05-01"],
            "independence_day": ["2026-08-14"],
            "iqbal_day": ["2026-11-09"],
            "quaid_e_azam_day": ["2026-12-25"],
        }
        return holidays

    def create_seasonal_features(self, df, date_column="date"):
        # Ensure date column exists and is datetime
        if date_column not in df.columns:
            print(f"Warning: {date_column} column not found. Creating dummy dates...")
            df[date_column] = pd.date_range("2024-01-01", periods=len(df), freq="D")

        df[date_column] = pd.to_datetime(df[date_column])

        df["month"] = df[date_column].dt.month
        df["quarter"] = df[date_column].dt.quarter
        df["day_of_week"] = df[date_column].dt.dayofweek
        df["week_of_year"] = df[date_column].dt.isocalendar().week
        df["is_weekend"] = (df[date_column].dt.dayofweek >= 5).astype(int)

        def get_season(month):
            if month in [12, 1, 2]:
                return "winter"
            elif month in [3, 4, 5]:
                return "spring"
            elif month in [6, 7, 8]:
                return "summer"
            elif month in [9, 10, 11]:
                return "autumn"

        df["season"] = df["month"].apply(get_season)

        # Create holiday flags safely
        df["is_eid_ul_fitr"] = (
            df[date_column]
            .isin([pd.to_datetime(date) for date in self.holidays["eid_ul_fitr"]])
            .astype(int)
        )
        df["is_eid_ul_azha"] = (
            df[date_column]
            .isin([pd.to_datetime(date) for date in self.holidays["eid_ul_azha"]])
            .astype(int)
        )
        df["is_independence_day"] = (
            df[date_column]
            .isin([pd.to_datetime(date) for date in self.holidays["independence_day"]])
            .astype(int)
        )

        # Create public holiday flag safely
        df["is_public_holiday"] = (
            df["is_eid_ul_fitr"] | df["is_eid_ul_azha"] | df["is_independence_day"]
        )

        # Add other holidays if they exist in the date range
        for holiday in ["ashura", "eid_milad_un_nabi"]:
            holiday_dates = [pd.to_datetime(date) for date in self.holidays[holiday]]
            if df[date_column].isin(holiday_dates).any():
                df["is_public_holiday"] = df["is_public_holiday"] | df[
                    date_column
                ].isin(holiday_dates).astype(int)

        df["days_until_eid"] = self.calculate_days_until_next_holiday(
            df[date_column], "eid_ul_fitr"
        )
        df["days_until_independence"] = self.calculate_days_until_next_holiday(
            df[date_column], "independence_day"
        )

        return df

    def calculate_days_until_next_holiday(self, dates, holiday_key):
        """Calculate days until next major holiday"""
        holiday_dates = [pd.to_datetime(date) for date in self.holidays[holiday_key]]
        days_until = []

        for date in dates:
            future_dates = [d for d in holiday_dates if d > date]
            if future_dates:
                next_holiday = min(future_dates)
                days_until.append((next_holiday - date).days)
            else:
                days_until.append(365)

        return days_until

    def create_product_features(self, df):
        # Safe price calculations
        if "original_price_clean" in df.columns and "discount_clean" in df.columns:
            # Avoid division by zero
            df["discount_percentage"] = (
                df["discount_clean"] / df["original_price_clean"].replace(0, np.nan)
            ).fillna(0).clip(0, 1) * 100
            df["price_ratio"] = (
                df["price_clean"] / df["original_price_clean"].replace(0, np.nan)
            ).fillna(1)
            df["savings_amount"] = df["original_price_clean"] - df["price_clean"]
        else:
            print("Warning: Missing price columns, creating basic features...")
            df["discount_percentage"] = 0
            df["price_ratio"] = 1
            df["savings_amount"] = 0

        df["is_high_discount"] = (df["discount_percentage"] > 30).astype(int)

        if "category" in df.columns and "brand" in df.columns:
            df["category_brand"] = df["category"] + "_" + df["brand"]

        # Safe text features
        if "title" in df.columns:
            df["title_length"] = df["title"].str.len().fillna(0)
        else:
            df["title_length"] = 0

        if "image_url" in df.columns:
            df["has_image"] = df["image_url"].notna().astype(int)
        else:
            df["has_image"] = 0

        return df

    def encode_categorical_features(self, df):
        """Encode categorical variables"""
        categorical_columns = [
            "brand",
            "category",
            "product_type",
            "primary_color",
            "material_type",
            "fit_type",
            "size_variant",
            "style_type",
            "season",
        ]

        for col in categorical_columns:
            if col in df.columns and df[col].notna().any():
                le = LabelEncoder()
                df[f"{col}_encoded"] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
                print(f"Encoded {col} -> {col}_encoded")
            else:
                print(f"Skipping {col} - not in dataframe or all null")

        return df

    def prepare_features(self, df, target_column="price_clean"):
        """Main method to prepare all features"""
        print("Starting data preprocessing...")
        print(f"Initial data shape: {df.shape}")

        df = self.create_seasonal_features(df)
        df = self.create_product_features(df)
        df = self.encode_categorical_features(df)

        feature_columns = [
            "month",
            "quarter",
            "day_of_week",
            "week_of_year",
            "is_weekend",
            "season_encoded",
            "is_eid_ul_fitr",
            "is_eid_ul_azha",
            "is_independence_day",
            "is_public_holiday",
            "days_until_eid",
            "days_until_independence",
            "discount_percentage",
            "price_ratio",
            "is_high_discount",
            "savings_amount",
            "title_length",
            "has_image",
        ]

        categorical_base = [
            "brand",
            "category",
            "product_type",
            "primary_color",
            "material_type",
            "fit_type",
            "size_variant",
            "style_type",
        ]

        for col in categorical_base:
            encoded_col = f"{col}_encoded"
            if encoded_col in df.columns:
                feature_columns.append(encoded_col)

        available_features = [col for col in feature_columns if col in df.columns]

        print(f"Using {len(available_features)} features for modeling")
        print(f"Final feature set: {available_features}")

        return df[available_features], df[target_column]

    def split_data(self, X, y, test_size=0.2, random_state=42):
        """Split data into train and test sets"""
        return train_test_split(X, y, test_size=test_size, random_state=random_state)


if __name__ == "__main__":
    try:
        # Correct path for testing
        data = pd.read_csv("../data/data.csv")
        print(f"Test data loaded: {data.shape}")

        preprocessor = HolidayPreprocessor()
        X, y = preprocessor.prepare_features(data)
        X_train, X_test, y_train, y_test = preprocessor.split_data(X, y)

        print(f"Training set shape: {X_train.shape}")
        print(f"Test set shape: {X_test.shape}")
        print("Data preprocessing completed successfully!")

    except Exception as e:
        print(f"Error in test: {e}")
        print("This is OK - your actual ML script will handle the real data path")
