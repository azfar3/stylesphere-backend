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
            "eid_ul_fitr": [
                "2025-03-31",
                "2025-04-01",
                "2025-04-02",
                "2026-03-21",
                "2026-03-22",
                "2026-03-23",
            ],
            "eid_ul_azha": [
                "2025-06-06",
                "2025-06-07",
                "2025-06-08",
                "2026-05-27",
                "2026-05-28",
            ],
            "ashura": ["2025-07-05", "2025-07-06", "2026-06-25", "2026-06-26"],
            "eid_milad_un_nabi": ["2025-09-05", "2026-08-25"],
            "kashmir_day": ["2025-02-05", "2026-02-05"],
            "pakistan_day": ["2025-03-23", "2026-03-23"],
            "labour_day": ["2025-05-01", "2026-05-01"],
            "independence_day": ["2025-08-14", "2026-08-14"],
            "iqbal_day": ["2025-11-09", "2026-11-09"],
            "quaid_e_azam_day": ["2025-12-25", "2026-12-25"],
        }
        return holidays

    def create_seasonal_features(self, df, date_column="date"):
        if date_column not in df.columns:
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

        df["is_public_holiday"] = (
            df["is_eid_ul_fitr"] | df["is_eid_ul_azha"] | df["is_independence_day"]
        )

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
        if "original_price_clean" in df.columns:
            df["original_price_category"] = pd.cut(
                df["original_price_clean"],
                bins=[0, 1000, 3000, 5000, 10000, float("inf")],
                labels=["budget", "affordable", "mid_range", "premium", "luxury"],
            )

        if "category" in df.columns and "brand" in df.columns:
            df["category_brand"] = df["category"] + "_" + df["brand"]

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
            "original_price_category",
        ]

        for col in categorical_columns:
            if col in df.columns and df[col].notna().any():
                le = LabelEncoder()
                df[f"{col}_encoded"] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le

        return df

    def prepare_features(self, df, target_type="sale_price"):
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
            "is_eid_ul_fitr",
            "is_eid_ul_azha",
            "is_independence_day",
            "is_public_holiday",
            "days_until_eid",
            "days_until_independence",
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
            "season",
            "original_price_category",
        ]

        for col in categorical_base:
            encoded_col = f"{col}_encoded"
            if encoded_col in df.columns:
                feature_columns.append(encoded_col)

        if "original_price_clean" in df.columns:
            feature_columns.append("original_price_clean")

        available_features = [col for col in feature_columns if col in df.columns]

        if target_type == "sale_price":
            y = df["price_clean"]
        else:
            y = df["discount_clean"]

        print(f"Using {len(available_features)} features for modeling")
        print(f"Target variable: {target_type}")
        print(f"Final feature set: {available_features}")

        return df[available_features], y

    def split_data(self, X, y, test_size=0.2, random_state=42):
        return train_test_split(X, y, test_size=test_size, random_state=random_state)
