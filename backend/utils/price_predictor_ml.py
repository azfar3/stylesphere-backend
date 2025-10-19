import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score, GridSearchCV
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import warnings
import sys
import os

# Add the path to your data_preprocessor module
sys.path.append(r"D:\StyleSphere\backend\data\preprocessing")

warnings.filterwarnings("ignore")


class PricePredictor:
    def __init__(self):
        self.models = {}
        self.model_performance = {}
        self.best_model = None
        self.feature_importance = None

    def initialize_models(self):
        """Initialize multiple models for comparison"""
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
        """Train all models and evaluate performance"""
        print("Training multiple models...")

        for name, model in self.models.items():
            print(f"Training {name}...")
            model.fit(X_train, y_train)

            # Predictions
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)

            # Calculate metrics
            train_mae = mean_absolute_error(y_train, y_pred_train)
            test_mae = mean_absolute_error(y_test, y_pred_test)
            train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
            test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
            train_r2 = r2_score(y_train, y_pred_train)
            test_r2 = r2_score(y_test, y_pred_test)

            # Store performance
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
        """Select the best performing model based on test R²"""
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
        """Analyze feature importance for tree-based models"""
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

            # Plot feature importance
            plt.figure(figsize=(10, 6))
            sns.barplot(data=importance_df.head(10), x="importance", y="feature")
            plt.title("Top 10 Feature Importance for Price Prediction")
            plt.tight_layout()
            plt.show()

    def predict_future_prices(self, X_future):
        """Make predictions on future data"""
        if self.best_model is None:
            raise ValueError("No model trained yet. Call train_models first.")

        return self.best_model.predict(X_future)

    def save_model(self, filepath="best_price_model.pkl"):
        """Save the trained model"""
        if self.best_model is not None:
            joblib.dump(self.best_model, filepath)
            print(f"Model saved to {filepath}")

    def generate_holiday_insights(self, X_test, y_test, y_pred):
        """Generate insights about holiday pricing patterns"""
        holiday_features = [
            col
            for col in X_test.columns
            if "is_" in col
            and "holiday" in col
            or "eid" in col
            or "independence" in col
        ]

        print("\nHoliday Pricing Insights:")
        for feature in holiday_features:
            if feature in X_test.columns:
                holiday_mask = X_test[feature] == 1
                if holiday_mask.any():
                    holiday_mae = mean_absolute_error(
                        y_test[holiday_mask], y_pred[holiday_mask]
                    )
                    non_holiday_mae = mean_absolute_error(
                        y_test[~holiday_mask], y_pred[~holiday_mask]
                    )

                    print(f"{feature}:")
                    print(f"  Holiday samples: {holiday_mask.sum()}")
                    print(f"  Holiday MAE: {holiday_mae:.2f}")
                    print(f"  Non-Holiday MAE: {non_holiday_mae:.2f}")


def load_and_preprocess_data(data_path):
    """Load and preprocess the actual dataset with flexible column handling"""
    print(f"Loading data from {data_path}...")

    try:
        # Load your actual dataset
        df = pd.read_csv(data_path)

        print("Data loaded successfully!")
        print(f"Dataset shape: {df.shape[0]} rows, {df.shape[1]} columns")
        print("Columns in your dataset:", df.columns.tolist())

        # Show basic info about the data
        print("\nFirst 3 rows:")
        print(df.head(3))

        # Map possible column names to expected names
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

        # Find and rename columns
        renamed_columns = []
        for target_col, possible_cols in column_mapping.items():
            for col in possible_cols:
                if col in df.columns and target_col not in df.columns:
                    df = df.rename(columns={col: target_col})
                    renamed_columns.append(f"'{col}' → '{target_col}'")
                    break

        if renamed_columns:
            print("Renamed columns:", renamed_columns)

        # Create missing required columns with sensible defaults
        if "date" not in df.columns:
            print("Creating dummy date column...")
            # Create realistic dates spanning the last year
            start_date = pd.Timestamp.now() - pd.DateOffset(days=365)
            df["date"] = pd.date_range(start=start_date, periods=len(df), freq="D")
            print("Created date column with realistic dates")

        if "price_clean" not in df.columns:
            # Try to find any numeric column that could be price
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                df["price_clean"] = df[numeric_cols[0]]  # Use first numeric column
                print(f"Using '{numeric_cols[0]}' as price_clean")
            else:
                raise ValueError(
                    "No price column found and no numeric columns available!"
                )

        if "original_price_clean" not in df.columns:
            print("Creating original_price_clean...")
            # If we have discount info, use it to calculate original price
            if "discount_clean" in df.columns:
                df["original_price_clean"] = df["price_clean"] + df["discount_clean"]
            else:
                df["original_price_clean"] = df["price_clean"] * 1.2  # 20% markup

        if "discount_clean" not in df.columns:
            print("Calculating discount_clean...")
            df["discount_clean"] = df["original_price_clean"] - df["price_clean"]

        # Final validation
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
        print("Final columns:", df.columns.tolist())

        return df

    except Exception as e:
        print(f"Error in data loading: {e}")
        raise


# Main training function
def main(data_path):
    try:
        from data_preprocessor import HolidayPreprocessor

        preprocessor_class = HolidayPreprocessor
        print("Successfully imported HolidayPreprocessor")
    except ImportError:
        print("Could not import preprocessor.")
        return None, None

    # Load and preprocess actual data
    df = load_and_preprocess_data(data_path)

    # Preprocess data
    print("Preprocessing data...")
    preprocessor = preprocessor_class()
    X, y = preprocessor.prepare_features(df)
    X_train, X_test, y_train, y_test = preprocessor.split_data(X, y)

    # Train models
    print("Initializing and training models...")
    predictor = PricePredictor()
    predictor.initialize_models()
    predictor.train_models(X_train, X_test, y_train, y_test)

    # Analyze results
    best_model_name = predictor.find_best_model()
    predictor.analyze_feature_importance(X.columns.tolist())

    # Generate predictions and insights
    y_pred = predictor.predict_future_prices(X_test)
    predictor.generate_holiday_insights(X_test, y_test, y_pred)

    # Save the model
    predictor.save_model("price_predictor.pkl")

    print("MODEL TRAINING COMPLETED SUCCESSFULLY!")

    return predictor, preprocessor


if __name__ == "__main__":
    data_file_path = "D:\\StyleSphere\\backend\\data\\data\\data.csv"

    predictor, preprocessor = main(data_file_path)
