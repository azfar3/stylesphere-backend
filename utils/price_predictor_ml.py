import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import warnings
import sys
import os

warnings.filterwarnings("ignore")


class PricePredictor:
    def __init__(self):
        self.models = {}
        self.model_performance = {}
        self.best_model = None
        self.feature_importance = None
        self.label_encoders = {}

    def initialize_models(self):
        self.models = {
            "random_forest": RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
            ),
            "gradient_boosting": GradientBoostingRegressor(
                n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42
            ),
            "linear_regression": LinearRegression(),
            "svr": SVR(kernel="rbf", C=1.0, epsilon=0.1),
        }

    def train_models(self, X_train, X_test, y_train, y_test):
        print("Training multiple models...")
        for name, model in self.models.items():
            print(f"Training {name}...")
            model.fit(X_train, y_train)
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)

            train_mae = mean_absolute_error(y_train, y_pred_train)
            test_mae = mean_absolute_error(y_test, y_pred_test)
            train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
            test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
            train_r2 = r2_score(y_train, y_pred_train)
            test_r2 = r2_score(y_test, y_pred_test)

            self.model_performance[name] = {
                "train_mae": train_mae,
                "test_mae": test_mae,
                "train_rmse": train_rmse,
                "test_rmse": test_rmse,
                "train_r2": train_r2,
                "test_r2": test_r2,
            }

            print(f"{name.upper()} Results:")
            print(f"  Train MAE: {train_mae:.2f}, Test MAE: {test_mae:.2f}")
            print(f"  Train R²: {train_r2:.4f}, Test R²: {test_r2:.4f}")
            print("-" * 50)

    def find_best_model(self):
        best_score = -np.inf
        best_model_name = None
        for name, performance in self.model_performance.items():
            if performance["test_r2"] > best_score:
                best_score = performance["test_r2"]
                best_model_name = name
        self.best_model = self.models[best_model_name]
        print(f"Best model: {best_model_name} with R²: {best_score:.4f}")
        return best_model_name

    def analyze_feature_importance(self, feature_names):
        if hasattr(self.best_model, "feature_importances_"):
            importance_df = pd.DataFrame(
                {
                    "feature": feature_names,
                    "importance": self.best_model.feature_importances_,
                }
            ).sort_values("importance", ascending=False)
            self.feature_importance = importance_df
            print("\nTop 10 Most Important Features:")
            print(importance_df.head(10))
            plt.figure(figsize=(10, 6))
            sns.barplot(data=importance_df.head(10), x="importance", y="feature")
            plt.title("Top 10 Feature Importance for Price Prediction")
            plt.tight_layout()
            plt.show()

    def predict_future_prices(self, X_future):
        if self.best_model is None:
            raise ValueError("No model trained yet. Call train_models first.")
        return self.best_model.predict(X_future)

    def save_model(self, filepath="best_price_model.pkl"):
        if self.best_model is not None:
            joblib.dump(self.best_model, filepath)
            print(f"Model saved to {filepath}")

    def create_future_feature_vector(
        self, product_features, occasion_date, occasion_name, feature_columns
    ):
        occasion_dt = pd.to_datetime(occasion_date)
        current_dt = pd.Timestamp.now()
        days_until = (occasion_dt - current_dt).days

        feature_dict = {}
        feature_dict["month"] = occasion_dt.month
        feature_dict["quarter"] = (occasion_dt.month - 1) // 3 + 1
        feature_dict["day_of_week"] = occasion_dt.dayofweek
        feature_dict["week_of_year"] = occasion_dt.isocalendar().week
        feature_dict["is_weekend"] = 1 if occasion_dt.dayofweek >= 5 else 0

        feature_dict["is_eid_ul_fitr"] = 1 if "eid" in occasion_name.lower() else 0
        feature_dict["is_eid_ul_azha"] = 1 if "azha" in occasion_name.lower() else 0
        feature_dict["is_independence_day"] = (
            1 if "independence" in occasion_name.lower() else 0
        )
        feature_dict["is_public_holiday"] = (
            1 if any(x in occasion_name.lower() for x in ["eid", "independence"]) else 0
        )

        feature_dict["days_until_eid"] = days_until
        feature_dict["days_until_independence"] = days_until

        feature_dict["title_length"] = product_features.get("title_length", 0)
        feature_dict["has_image"] = product_features.get("has_image", 1)

        if "original_price_clean" in feature_columns:
            feature_dict["original_price_clean"] = product_features.get(
                "original_price_clean", 0
            )

        for col in [
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
        ]:
            encoded_col = f"{col}_encoded"
            if encoded_col in feature_columns:
                feature_dict[encoded_col] = product_features.get(encoded_col, 0)

        feature_vector = [feature_dict.get(col, 0) for col in feature_columns]
        return feature_vector

    def combine_predictions(self, ml_price, gemini_insights, original_price):
        if not gemini_insights:
            return ml_price

        gemini_avg_discount = (
            gemini_insights["min_discount"] + gemini_insights["max_discount"]
        ) / 2
        gemini_price = original_price * (1 - gemini_avg_discount / 100)

        if gemini_insights["confidence"] == "high":
            final_price = 0.3 * ml_price + 0.7 * gemini_price
        elif gemini_insights["confidence"] == "medium":
            final_price = 0.6 * ml_price + 0.4 * gemini_price
        else:
            final_price = 0.8 * ml_price + 0.2 * gemini_price

        return max(0, min(final_price, original_price))

    def predict_for_occasions(
        self, product_features, occasions, feature_columns, gemini_analyzer=None
    ):
        if self.best_model is None:
            raise ValueError("No model trained yet. Call train_models first.")

        future_predictions = {}
        original_price = product_features.get("original_price_clean", 0)

        for occasion_name, occasion_date in occasions.items():
            try:
                future_feature_vector = self.create_future_feature_vector(
                    product_features, occasion_date, occasion_name, feature_columns
                )
                ml_price = self.best_model.predict([future_feature_vector])[0]

                gemini_insights = None
                if gemini_analyzer:
                    gemini_insights = gemini_analyzer.get_occasion_insights(
                        product_features.get("title", ""),
                        product_features.get("brand", ""),
                        product_features.get("category", ""),
                        occasion_name,
                    )

                final_price = self.combine_predictions(
                    ml_price, gemini_insights, original_price
                )
                final_discount = ((original_price - final_price) / original_price) * 100

                future_predictions[occasion_name] = {
                    "predicted_price": round(final_price, 2),
                    "predicted_discount": round(final_discount, 1),
                    "ml_price": round(ml_price, 2),
                    "gemini_insights": gemini_insights,
                    "occasion_date": occasion_date,
                    "original_price": original_price,
                }
            except Exception as e:
                print(f"Error predicting for {occasion_name}: {e}")
                future_predictions[occasion_name] = {
                    "error": str(e),
                    "occasion_date": occasion_date,
                }
        return future_predictions


def load_and_preprocess_data(data_path):
    print(f"Loading data from {data_path}...")
    try:
        df = pd.read_csv(data_path)
        print("Data loaded successfully!")
        print(f"Dataset shape: {df.shape[0]} rows, {df.shape[1]} columns")
        print("Columns in your dataset:", df.columns.tolist())
        print("\nFirst 3 rows:")
        print(df.head(3))

        column_mapping = {
            "date": [
                "date",
                "created_at",
                "timestamp",
                "order_date",
                "sale_date",
                "Date",
                "DATE",
            ],
            "price_clean": [
                "price_clean",
                "price",
                "sale_price",
                "current_price",
                "Price",
                "PRICE",
            ],
            "original_price_clean": [
                "original_price_clean",
                "original_price",
                "regular_price",
                "Original_Price",
            ],
            "discount_clean": [
                "discount_clean",
                "discount",
                "discount_amount",
                "Discount",
                "DISCOUNT",
            ],
        }

        renamed_columns = []
        for target_col, possible_cols in column_mapping.items():
            for col in possible_cols:
                if col in df.columns and target_col not in df.columns:
                    df = df.rename(columns={col: target_col})
                    renamed_columns.append(f"'{col}' → '{target_col}'")
                    break

        if renamed_columns:
            print("Renamed columns:", renamed_columns)

        if "date" not in df.columns:
            print("Creating dummy date column...")
            start_date = pd.Timestamp.now() - pd.DateOffset(days=365)
            df["date"] = pd.date_range(start=start_date, periods=len(df), freq="D")

        if "price_clean" not in df.columns:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                df["price_clean"] = df[numeric_cols[0]]
                print(f"Using '{numeric_cols[0]}' as price_clean")
            else:
                raise ValueError(
                    "No price column found and no numeric columns available!"
                )

        if "original_price_clean" not in df.columns:
            print("Creating original_price_clean...")
            if "discount_clean" in df.columns:
                df["original_price_clean"] = df["price_clean"] + df["discount_clean"]
            else:
                df["original_price_clean"] = df["price_clean"] * 1.2

        if "discount_clean" not in df.columns:
            print("Calculating discount_clean...")
            df["discount_clean"] = df["original_price_clean"] - df["price_clean"]

        required_columns = [
            "price_clean",
            "original_price_clean",
            "discount_clean",
            "date",
        ]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(
                f"Missing required columns after processing: {missing_columns}"
            )

        print(f"Final dataset ready: {df.shape[0]} rows, {df.shape[1]} columns")
        return df

    except Exception as e:
        print(f"Error in data loading: {e}")
        raise


def main(data_path):
    try:
        from data_preprocessor import HolidayPreprocessor
        from gemini_analyzer import GeminiOccasionAnalyzer

        preprocessor_class = HolidayPreprocessor
        print("Successfully imported HolidayPreprocessor")
    except ImportError as e:
        print(f"Import error: {e}")
        return None, None

    df = load_and_preprocess_data(data_path)
    print("Preprocessing data...")
    preprocessor = preprocessor_class()
    X, y = preprocessor.prepare_features(df, target_type="sale_price")
    X_train, X_test, y_train, y_test = preprocessor.split_data(X, y)

    print("Initializing and training models...")
    predictor = PricePredictor()
    predictor.initialize_models()
    predictor.train_models(X_train, X_test, y_train, y_test)

    best_model_name = predictor.find_best_model()
    predictor.analyze_feature_importance(X.columns.tolist())
    predictor.save_model("price_predictor.pkl")

    gemini_analyzer = GeminiOccasionAnalyzer(
        api_key="AIzaSyD9dkoJRN78uiRWhC9gcCo0EuM0jW7WtX4"
    )

    sample_product = {
        "brand": "Outfitters",
        "category": "men",
        "original_price_clean": 2990,
        "price_clean": 2490,
        "title": "Slogan Print T-Shirt",
        "title_length": 18,
        "has_image": 1,
    }

    for col in ["brand", "category"]:
        encoded_col = f"{col}_encoded"
        if (
            hasattr(preprocessor, "label_encoders")
            and col in preprocessor.label_encoders
        ):
            sample_product[encoded_col] = preprocessor.label_encoders[col].transform(
                [sample_product[col]]
            )[0]
        else:
            sample_product[encoded_col] = 0

    upcoming_occasions = {
        "eid_ul_fitr": "2026-03-21",
        "independence_day": "2026-08-14",
        "christmas": "2026-12-25",
    }

    occasion_predictions = predictor.predict_for_occasions(
        sample_product, upcoming_occasions, X.columns.tolist(), gemini_analyzer
    )

    print("\n" + "=" * 60)
    print("OCCASION PRICE PREDICTIONS")
    print("=" * 60)
    original_price = sample_product["original_price_clean"]
    current_price = sample_product["price_clean"]
    print(f"Original Price: {original_price} PKR")
    print(f"Current Price: {current_price} PKR")
    print("\nPredicted Occasion Prices (from Original Price):")
    print("-" * 50)

    for occasion, prediction in occasion_predictions.items():
        if "error" not in prediction:
            print(
                f"{occasion.upper():<20} {prediction['predicted_price']:>6} PKR ({prediction['predicted_discount']}% off)"
            )
            if prediction.get("gemini_insights"):
                insights = prediction["gemini_insights"]
                print(
                    f"Gemini: {insights['min_discount']}-{insights['max_discount']}% ({insights['confidence']} confidence)"
                )
        else:
            print(f"{occasion.upper():<20} Error: {prediction['error']}")

    print("Model Training Completed.")
    return predictor, preprocessor


if __name__ == "__main__":
    data_file_path = "../data/data/data.csv"
    predictor, preprocessor = main(data_file_path)
