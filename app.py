from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
from datetime import datetime
import logging
from utils.gemini_analyzer import GeminiOccasionAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


class PredictionService:
    def __init__(self):
        self.model = None
        self.feature_columns = None
        self.gemini_analyzer = GeminiOccasionAnalyzer()
        self.load_model()

    def load_model(self):
        try:
            self.model = joblib.load("utils/price_predictor.pkl")
            if hasattr(self.model, "feature_names_in_"):
                print("Model was trained with features:", self.model.feature_names_in_)
                print("Number of features expected:", len(self.model.feature_names_in_))
            else:
                print("Model doesn't have feature names information")

            self.feature_columns = [
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
                "price_ratio",
                "is_high_discount",
                "savings_amount",
                "title_length",
                "has_image",
                "brand_encoded",
                "category_encoded",
            ]
            print("Current feature columns:", len(self.feature_columns))
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None

    def get_brand_encoding(self, brand):
        brand_map = {
            "outfitters": 0,
            "cougar": 1,
            "gulahmed": 2,
            "one": 3,
            "engine": 4,
            "unknown": 5,
        }
        return brand_map.get(brand.lower(), 5)

    def get_category_encoding(self, category):
        category_map = {
            "clothing": 0,
            "shoes": 1,
            "accessories": 2,
            "electronics": 3,
            "beauty": 4,
            "home": 5,
            "unknown": 6,
        }
        return category_map.get(category.lower(), 6)

    def prepare_product_features(self, product_data, occasion_date, occasion_name):
        occasion_dt = pd.to_datetime(occasion_date)
        current_dt = pd.Timestamp.now()

        brand_encoded = self.get_brand_encoding(product_data.get("brand", "unknown"))
        category_encoded = self.get_category_encoding(
            product_data.get("category", "unknown")
        )

        original_price = product_data.get("original_price_clean") or product_data.get(
            "price_clean", 1
        )
        price_ratio = product_data.get("price_clean", 1) / original_price

        feature_dict = {
            "month": occasion_dt.month,
            "quarter": (occasion_dt.month - 1) // 3 + 1,
            "day_of_week": occasion_dt.dayofweek,
            "week_of_year": occasion_dt.isocalendar().week,
            "is_weekend": 1 if occasion_dt.dayofweek >= 5 else 0,
            "season_encoded": self.get_season_encoded(occasion_dt.month),
            "is_eid_ul_fitr": 1 if "eid_ul_fitr" in occasion_name.lower() else 0,
            "is_eid_ul_azha": 1 if "eid_ul_azha" in occasion_name.lower() else 0,
            "is_independence_day": 1 if "independence" in occasion_name.lower() else 0,
            "is_public_holiday": (
                1
                if any(
                    x in occasion_name.lower()
                    for x in ["eid", "independence", "pakistan"]
                )
                else 0
            ),
            "days_until_eid": self.days_until_next_holiday(current_dt, "2025-03-31"),
            "days_until_independence": self.days_until_next_holiday(
                current_dt, "2025-08-14"
            ),
            "price_ratio": price_ratio,
            "is_high_discount": product_data.get("is_high_discount", 0),
            "savings_amount": product_data.get("savings_amount", 0),
            "title_length": product_data.get("title_length", 0),
            "has_image": product_data.get("has_image", 1),
            "brand_encoded": brand_encoded,
            "category_encoded": category_encoded,
            "product_type_encoded": self.get_product_type_encoding(
                product_data.get("product_type", "unknown")
            ),
            "primary_color_encoded": self.get_color_encoding(
                product_data.get("primary_color", "unknown")
            ),
            "material_type_encoded": self.get_material_encoding(
                product_data.get("material_type", "unknown")
            ),
            "fit_type_encoded": self.get_fit_encoding(
                product_data.get("fit_type", "unknown")
            ),
            "size_variant_encoded": self.get_size_encoding(
                product_data.get("size_variant", "unknown")
            ),
            "style_type_encoded": self.get_style_encoding(
                product_data.get("style_type", "unknown")
            ),
        }

        expected_features = [
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
            "price_ratio",
            "is_high_discount",
            "savings_amount",
            "title_length",
            "has_image",
            "brand_encoded",
            "category_encoded",
            "product_type_encoded",
            "primary_color_encoded",
            "material_type_encoded",
            "fit_type_encoded",
            "size_variant_encoded",
            "style_type_encoded",
        ]

        feature_vector = [feature_dict.get(col, 0) for col in expected_features]

        print(f"Prepared {len(feature_vector)} features for {occasion_name}")
        return feature_vector

    def get_product_type_encoding(self, product_type):
        type_map = {
            "t-shirts": 0,
            "shirts": 1,
            "pants": 2,
            "shoes": 3,
            "accessories": 4,
            "dresses": 5,
            "unknown": 6,
        }
        return type_map.get(product_type.lower(), 6)

    def get_color_encoding(self, color):
        color_map = {
            "black": 0,
            "white": 1,
            "blue": 2,
            "red": 3,
            "green": 4,
            "yellow": 5,
            "multi/unknown": 6,
            "pink": 7,
            "gray": 8,
            "brown": 9,
        }
        return color_map.get(color.lower(), 6)

    def get_material_encoding(self, material):
        material_map = {
            "cotton": 0,
            "polyester": 1,
            "denim": 2,
            "silk": 3,
            "wool": 4,
            "linen": 5,
            "printed cotton": 6,
            "unknown": 7,
        }
        return material_map.get(material.lower(), 7)

    def get_fit_encoding(self, fit):
        fit_map = {"regular": 0, "slim": 1, "loose": 2, "tight": 3, "unknown": 4}
        return fit_map.get(fit.lower(), 4)

    def get_size_encoding(self, size):
        size_map = {
            "s, m, l, xl": 0,
            "xs, s, m, l, xl": 1,
            "m, l, xl": 2,
            "one size": 3,
            "unknown": 4,
        }
        return size_map.get(size.lower(), 4)

    def get_style_encoding(self, style):
        style_map = {
            "slogan print": 0,
            "plain": 1,
            "printed": 2,
            "embroidered": 3,
            "striped": 4,
            "checkered": 5,
            "unknown": 6,
        }
        return style_map.get(style.lower(), 6)

    def get_season_encoded(self, month):
        if month in [12, 1, 2]:
            return 0
        elif month in [3, 4, 5]:
            return 1
        elif month in [6, 7, 8]:
            return 2
        else:
            return 3

    def days_until_next_holiday(self, current_date, holiday_date):
        holiday_dt = pd.to_datetime(holiday_date)
        if holiday_dt > current_date:
            return (holiday_dt - current_date).days
        return 365

    def combine_predictions(self, ml_discount, gemini_insights):
        if not gemini_insights:
            return max(5, min(ml_discount, 70))

        gemini_avg = (
            gemini_insights["min_discount"] + gemini_insights["max_discount"]
        ) / 2

        if gemini_insights["confidence"] == "high":
            final_discount = 0.3 * ml_discount + 0.7 * gemini_avg
        elif gemini_insights["confidence"] == "medium":
            final_discount = 0.6 * ml_discount + 0.4 * gemini_avg
        else:
            final_discount = 0.8 * ml_discount + 0.2 * gemini_avg

        return max(5, min(final_discount, 70))

    def predict_for_product(self, product_data):
        if self.model is None:
            return {"error": "Model not loaded"}

        occasions = {
            "eid_ul_fitr": "2026-03-21",
            "independence_day": "2026-08-14",
            "christmas": "2026-12-25",
            "eid_ul_azha": "2026-05-27",
        }

        predictions = {}
        current_price = product_data.get("price_clean", 0)

        for occasion_name, occasion_date in occasions.items():
            try:
                features = self.prepare_product_features(
                    product_data, occasion_date, occasion_name
                )
                ml_discount = self.model.predict([features])[0]

                gemini_insights = self.gemini_analyzer.get_occasion_insights(
                    product_data.get("title", ""),
                    product_data.get("brand", ""),
                    product_data.get("category", ""),
                    occasion_name,
                )

                final_discount = self.combine_predictions(ml_discount, gemini_insights)
                predicted_price = current_price * (1 - final_discount / 100)

                predictions[occasion_name] = {
                    "predicted_price": round(predicted_price, 2),
                    "predicted_discount": round(final_discount, 2),
                    "savings": round(current_price - predicted_price, 2),
                    "occasion_date": occasion_date,
                    "gemini_confidence": gemini_insights.get("confidence", "medium"),
                    "reasoning": gemini_insights.get(
                        "reasoning", "AI-powered prediction"
                    ),
                }

                logger.info(f"{occasion_name}: {final_discount}% discount")

            except Exception as e:
                logger.error(f"Prediction failed for {occasion_name}: {e}")
                predictions[occasion_name] = {"error": str(e)}

        return predictions


prediction_service = PredictionService()


@app.route("/api/predict", methods=["POST"])
def predict_prices():
    try:
        product_data = request.json
        logger.info(
            f"Prediction request for: {product_data.get('title', 'Unknown product')}"
        )

        predictions = prediction_service.predict_for_product(product_data)
        return jsonify(
            {
                "success": True,
                "current_price": product_data.get("price_clean", 0),
                "predictions": predictions,
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Prediction endpoint error: {e}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify(
        {
            "status": "healthy",
            "model_loaded": prediction_service.model is not None,
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/", methods=["GET"])
def home():
    return jsonify(
        {
            "message": "Price Prediction API",
            "version": "1.0.0",
            "endpoints": {
                "health": "/api/health (GET)",
                "predict": "/api/predict (POST)",
            },
        }
    )


if __name__ == "__main__":
    logger.info("Starting Flask server...")
    app.run(debug=True, port=8000, host="0.0.0.0")
