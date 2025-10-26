import pickle
import pandas as pd
import numpy as np
import sys
import json
import os
from datetime import datetime, timedelta
import joblib


class SimpleMLPredictor:
    def __init__(self, model_path="price_predictor.pkl"):
        self.model = None
        self.model_path = model_path
        self.load_model()

    def load_model(self):
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                print("ML model loaded successfully")
                return True
            else:
                print(f"Model file not found at: {self.model_path}")
                alternative_paths = [
                    "../models/price_predictor.pkl",
                    "price_predictor.pkl",
                    "./price_predictor.pkl",
                ]

                for path in alternative_paths:
                    if os.path.exists(path):
                        self.model = joblib.load(path)
                        print(f"ML model loaded from: {path}")
                        return True

                print("Model not found in any common locations")
                return False

        except Exception as e:
            print(f"Error loading model: {e}")
            return False

    def create_basic_features(self, product_data):
        try:
            current_price = float(product_data.get("price", 0))
            original_price = float(
                product_data.get("originalPrice", current_price * 1.2)
            )
            discount = float(product_data.get("discount", 0))

            discount_percent = (
                (discount / original_price * 100) if original_price > 0 else 0
            )
            price_ratio = current_price / original_price if original_price > 0 else 1

            now = datetime.now()
            month = now.month
            day_of_week = now.weekday()
            is_weekend = 1 if day_of_week >= 5 else 0
            quarter = (month - 1) // 3 + 1

            category = str(product_data.get("category", "unknown")).lower()
            category_features = {}

            common_categories = [
                "electronics",
                "fashion",
                "clothing",
                "home",
                "kitchen",
                "beauty",
                "sports",
                "books",
                "toys",
                "automotive",
            ]

            for cat in common_categories:
                category_features[f"cat_{cat}"] = 1 if cat in category else 0

            brand = str(product_data.get("brand", "unknown")).lower()
            brand_hash = hash(brand) % 100

            features = {
                "price_clean": current_price,
                "original_price_clean": original_price,
                "discount_clean": discount,
                "discount_percent": discount_percent,
                "price_ratio": price_ratio,
                "month": month,
                "day_of_week": day_of_week,
                "is_weekend": is_weekend,
                "quarter": quarter,
                "brand_encoded": brand_hash,
                "description_length": len(str(product_data.get("description", ""))),
                "name_length": len(str(product_data.get("name", ""))),
            }
            features.update(category_features)
            features.update(self._get_seasonal_features(month))

            return pd.DataFrame([features])

        except Exception as e:
            print(f"Error creating features: {e}")
            return None

    def _get_seasonal_features(self, month):
        seasonal_features = {}

        seasonal_features["is_holiday_season"] = 1 if month in [11, 12] else 0
        seasonal_features["is_summer"] = 1 if month in [6, 7, 8] else 0
        seasonal_features["is_winter"] = 1 if month in [12, 1, 2] else 0

        seasonal_features["is_q1"] = 1 if month in [1, 2, 3] else 0
        seasonal_features["is_q2"] = 1 if month in [4, 5, 6] else 0
        seasonal_features["is_q3"] = 1 if month in [7, 8, 9] else 0
        seasonal_features["is_q4"] = 1 if month in [10, 11, 12] else 0

        return seasonal_features

    def predict_price(self, product_data, target_days=30):
        if self.model is None:
            return self._fallback_prediction(product_data, target_days)

        try:
            features_df = self.create_basic_features(product_data)
            if features_df is None:
                return self._fallback_prediction(product_data, target_days)

            predicted_price = self.model.predict(features_df)[0]
            current_price = product_data.get("price", 0)
            predicted_price = max(predicted_price, current_price * 0.5)
            predicted_price = min(predicted_price, current_price * 2.0)
            price_change_percent = (
                (predicted_price - current_price) / current_price
            ) * 100

            return {
                "success": True,
                "prediction": {
                    "current_price": round(current_price, 2),
                    "predicted_price": round(predicted_price, 2),
                    "confidence": self._calculate_confidence(price_change_percent),
                    "trend": (
                        "increasing"
                        if price_change_percent > 2
                        else "decreasing" if price_change_percent < -2 else "stable"
                    ),
                    "price_change_percent": round(price_change_percent, 2),
                    "target_date": (
                        datetime.now() + timedelta(days=target_days)
                    ).strftime("%Y-%m-%d"),
                    "factors": self._analyze_factors(
                        product_data, price_change_percent
                    ),
                    "recommendation": self._generate_recommendation(
                        price_change_percent, predicted_price, current_price
                    ),
                },
                "metadata": {
                    "model_type": "ML_Model",
                    "prediction_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "target_days": target_days,
                    "feature_count": (
                        len(features_df.columns) if features_df is not None else 0
                    ),
                },
            }

        except Exception as e:
            print(f"ML prediction error: {e}")
            return self._fallback_prediction(product_data, target_days)

    def _calculate_confidence(self, price_change_percent):
        change_magnitude = abs(price_change_percent)

        if change_magnitude < 5:
            return 85
        elif change_magnitude < 15:
            return 75
        elif change_magnitude < 25:
            return 65
        else:
            return 55

    def _analyze_factors(self, product_data, price_change):
        factors = []
        current_price = product_data.get("price", 0)
        discount = product_data.get("discount", 0)
        category = product_data.get("category", "").lower()
        if discount > 10:
            factors.append(
                {
                    "factor": "High Discount",
                    "impact": "positive" if price_change < 0 else "negative",
                    "weight": 0.3,
                    "description": f"Large current discount ({discount}%) may affect future pricing",
                }
            )
        if any(cat in category for cat in ["electronics", "phone", "laptop"]):
            factors.append(
                {
                    "factor": "Electronics Category",
                    "impact": "volatile",
                    "weight": 0.25,
                    "description": "Electronics prices can be volatile due to tech updates",
                }
            )
        elif any(cat in category for cat in ["fashion", "clothing", "apparel"]):
            factors.append(
                {
                    "factor": "Fashion Category",
                    "impact": "seasonal",
                    "weight": 0.2,
                    "description": "Fashion items often follow seasonal trends",
                }
            )
        if current_price > 1000:
            factors.append(
                {
                    "factor": "Premium Product",
                    "impact": "stable",
                    "weight": 0.15,
                    "description": "High-value items may have more stable pricing",
                }
            )
        current_month = datetime.now().month
        if current_month in [11, 12]:
            factors.append(
                {
                    "factor": "Holiday Season",
                    "impact": "positive",
                    "weight": 0.2,
                    "description": "Holiday season often affects pricing strategies",
                }
            )

        return factors

    def _generate_recommendation(self, price_change, predicted_price, current_price):
        """Generate buying recommendation"""
        if price_change < -15:
            return "EXCELLENT BUY - Significant price drop expected!"
        elif price_change < -8:
            return "Good deal expected - Wait for better price"
        elif price_change < -3:
            return "Fair price coming - Consider waiting"
        elif price_change > 20:
            return "BUY NOW - Prices expected to rise significantly!"
        elif price_change > 10:
            return "Buy soon - Prices trending upward"
        elif abs(price_change) < 5:
            return "Prices stable - Buy when convenient"
        else:
            return "Monitor prices - Some movement expected"

    def _fallback_prediction(self, product_data, target_days):
        """Fallback when ML model fails"""
        current_price = product_data.get("price", 0)
        base_change = np.random.normal(-2, 5)
        predicted_price = current_price * (1 + base_change / 100)
        predicted_price = max(predicted_price, current_price * 0.7)
        predicted_price = min(predicted_price, current_price * 1.3)

        price_change = ((predicted_price - current_price) / current_price) * 100

        return {
            "success": True,
            "prediction": {
                "current_price": round(current_price, 2),
                "predicted_price": round(predicted_price, 2),
                "confidence": 60.0,
                "trend": "stable",
                "price_change_percent": round(price_change, 2),
                "target_date": (datetime.now() + timedelta(days=target_days)).strftime(
                    "%Y-%m-%d"
                ),
                "factors": [
                    {
                        "factor": "Rule-based Estimate",
                        "impact": "neutral",
                        "weight": 1.0,
                        "description": "Using fallback prediction method",
                    }
                ],
                "recommendation": "Limited prediction data available",
            },
            "metadata": {
                "model_type": "fallback",
                "prediction_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "target_days": target_days,
                "note": "ML model not available",
            },
        }


def main():
    try:
        input_data = sys.stdin.read()
        request_data = json.loads(input_data)
        product_data = request_data["product_data"]
        target_days = request_data.get("target_days", 30)
        predictor = SimpleMLPredictor()
        result = predictor.predict_price(product_data, target_days)
        print(json.dumps(result))

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "prediction": {
                "current_price": product_data.get("price", 0),
                "predicted_price": product_data.get("price", 0),
                "confidence": 50.0,
                "trend": "unknown",
                "price_change_percent": 0,
                "factors": [],
                "recommendation": "ML service error",
            },
        }
        print(json.dumps(error_result))


if __name__ == "__main__":
    main()
