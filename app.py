from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
from datetime import datetime
import logging
from utils.gemini_analyzer import GeminiOccasionAnalyzer
from utils.styling_advisor import StyleAdvisorService
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


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
                self.feature_columns = list(self.model.feature_names_in_)
            else:
                print("Model doesn't have feature names information")
                self.feature_columns = [
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
                    "brand_encoded",
                    "category_encoded",
                    "product_type_encoded",
                    "primary_color_encoded",
                    "material_type_encoded",
                    "fit_type_encoded",
                    "size_variant_encoded",
                    "style_type_encoded",
                    "season_encoded",
                    "original_price_category_encoded",
                    "original_price_clean",
                ]

            print("Current feature columns:", len(self.feature_columns))
            print("Feature columns:", self.feature_columns)
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None

    def get_upcoming_occasions(self, count=3):
        current_date = pd.Timestamp.now()

        all_occasions = {
            "eid_ul_fitr": ["2025-03-31", "2026-03-21", "2027-03-11"],
            "eid_ul_azha": ["2025-06-06", "2026-05-27", "2027-05-16"],
            "independence_day": ["2025-08-14", "2026-08-14", "2027-08-14"],
            "christmas": ["2025-12-25", "2026-12-25", "2027-12-25"],
            "new_year": ["2026-01-01", "2027-01-01", "2028-01-01"],
            "pakistan_day": ["2025-03-23", "2026-03-23", "2027-03-23"],
            "labour_day": ["2025-05-01", "2026-05-01", "2027-05-01"],
        }

        upcoming = []
        for occasion_name, dates in all_occasions.items():
            for date_str in dates:
                occasion_date = pd.to_datetime(date_str)
                if occasion_date > current_date:
                    days_until = (occasion_date - current_date).days
                    upcoming.append(
                        {
                            "name": occasion_name,
                            "date": date_str,
                            "days_until": days_until,
                            "occasion_date": occasion_date,
                        }
                    )

        upcoming.sort(key=lambda x: x["occasion_date"])
        next_occasions = upcoming[:count]

        occasions_dict = {item["name"]: item["date"] for item in next_occasions}

        logger.info(
            f"Next {count} upcoming occasions: {[item['name'] for item in next_occasions]}"
        )
        return occasions_dict

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

        original_price = product_data.get("original_price_clean") or product_data.get(
            "price_clean", 1
        )

        days_until_occasion = (occasion_dt - current_dt).days

        feature_dict = {
            "month": occasion_dt.month,
            "quarter": (occasion_dt.month - 1) // 3 + 1,
            "day_of_week": occasion_dt.dayofweek,
            "week_of_year": occasion_dt.isocalendar().week,
            "is_weekend": 1 if occasion_dt.dayofweek >= 5 else 0,
            "is_eid_ul_fitr": 1 if "eid_ul_fitr" in occasion_name.lower() else 0,
            "is_eid_ul_azha": 1 if "eid_ul_azha" in occasion_name.lower() else 0,
            "is_independence_day": 1 if "independence" in occasion_name.lower() else 0,
            "is_public_holiday": (
                1
                if any(
                    x in occasion_name.lower()
                    for x in [
                        "eid",
                        "independence",
                        "pakistan",
                        "christmas",
                        "new_year",
                    ]
                )
                else 0
            ),
            "days_until_eid": self.get_days_until_specific_holiday(
                current_dt, ["eid_ul_fitr", "eid_ul_azha"]
            ),
            "days_until_independence": self.get_days_until_specific_holiday(
                current_dt, ["independence_day", "pakistan_day"]
            ),
            "title_length": product_data.get("title_length", 0),
            "has_image": product_data.get("has_image", 1),
            "brand_encoded": self.get_brand_encoding(
                product_data.get("brand", "unknown")
            ),
            "category_encoded": self.get_category_encoding(
                product_data.get("category", "unknown")
            ),
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
            "season_encoded": self.get_season_encoded(occasion_dt.month),
            "original_price_category_encoded": self.get_price_category_encoding(
                original_price
            ),
            "original_price_clean": original_price,
        }

        feature_vector = [feature_dict.get(col, 0) for col in self.feature_columns]

        print(
            f"Prepared {len(feature_vector)} features for {occasion_name} on {occasion_date}"
        )
        return feature_vector

    def get_days_until_specific_holiday(self, current_date, holiday_types):
        all_occasions = {
            "eid_ul_fitr": ["2025-03-31", "2026-03-21", "2027-03-11"],
            "eid_ul_azha": ["2025-06-06", "2026-05-27", "2027-05-16"],
            "independence_day": ["2025-08-14", "2026-08-14", "2027-08-14"],
            "pakistan_day": ["2025-03-23", "2026-03-23", "2027-03-23"],
        }

        min_days = 365
        for holiday_type in holiday_types:
            if holiday_type in all_occasions:
                for date_str in all_occasions[holiday_type]:
                    holiday_date = pd.to_datetime(date_str)
                    if holiday_date > current_date:
                        days_until = (holiday_date - current_date).days
                        min_days = min(min_days, days_until)

        return min_days

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

    def get_price_category_encoding(self, price):
        if price <= 1000:
            return 0
        elif price <= 3000:
            return 1
        elif price <= 5000:
            return 2
        elif price <= 10000:
            return 3
        else:
            return 4

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

    def predict_for_product(self, product_data):
        if self.model is None:
            return {"error": "Model not loaded"}

        occasions = self.get_upcoming_occasions(count=3)

        if not occasions:
            return {"error": "No upcoming occasions found"}

        predictions = {}
        original_price = product_data.get("original_price_clean") or product_data.get(
            "price_clean", 0
        )

        for occasion_name, occasion_date in occasions.items():
            try:
                features = self.prepare_product_features(
                    product_data, occasion_date, occasion_name
                )
                ml_price = self.model.predict([features])[0]

                gemini_insights = self.gemini_analyzer.get_occasion_insights(
                    product_data.get("title", ""),
                    product_data.get("brand", ""),
                    product_data.get("category", ""),
                    occasion_name,
                )

                final_price = self.combine_predictions(
                    ml_price, gemini_insights, original_price
                )
                final_discount = ((original_price - final_price) / original_price) * 100

                predictions[occasion_name] = {
                    "predicted_price": round(final_price, 2),
                    "predicted_discount": round(final_discount, 2),
                    "savings": round(original_price - final_price, 2),
                    "occasion_date": occasion_date,
                    "days_until": (
                        pd.to_datetime(occasion_date) - pd.Timestamp.now()
                    ).days,
                    "original_price": original_price,
                    "gemini_confidence": gemini_insights.get("confidence", "medium"),
                    "reasoning": gemini_insights.get(
                        "reasoning", "AI-powered prediction"
                    ),
                }

                logger.info(
                    f"{occasion_name} ({occasion_date}): {final_price} PKR ({final_discount:.1f}% discount)"
                )

            except Exception as e:
                logger.error(f"Prediction failed for {occasion_name}: {e}")
                predictions[occasion_name] = {"error": str(e)}

        return predictions


prediction_service = PredictionService()
style_advisor = StyleAdvisorService(GEMINI_API_KEY)


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
                "original_price": product_data.get("original_price_clean")
                or product_data.get("price_clean", 0),
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


@app.route("/api/occasions", methods=["GET"])
def get_upcoming_occasions():
    try:
        occasions = prediction_service.get_upcoming_occasions(count=3)
        return jsonify(
            {
                "success": True,
                "occasions": occasions,
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Occasions endpoint error: {e}")
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


@app.route("/api/style-recommendation", methods=["POST"])
def get_style_recommendation():
    try:
        user_profile = request.json
        logger.info(
            f"Style recommendation request for: {user_profile.get('gender', 'Unknown')} user for {user_profile.get('event', 'Unknown event')}"
        )

        result = style_advisor.get_style_recommendation(user_profile)

        if "error" in result:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": result["error"],
                        "details": result.get("details"),
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                400,
            )

        return jsonify(
            {"success": True, **result, "timestamp": datetime.now().isoformat()}
        )

    except Exception as e:
        logger.error(f"Style recommendation endpoint error: {e}")
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


@app.route("/api/analyze-image", methods=["POST"])
def analyze_image():
    try:
        if "file" not in request.files:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "No file uploaded",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                400,
            )

        file = request.files["file"]

        if file.filename == "":
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "No file selected",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                400,
            )

        allowed_extensions = {"png", "jpg", "jpeg", "gif"}
        if (
            "." in file.filename
            and file.filename.rsplit(".", 1)[1].lower() not in allowed_extensions
        ):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Invalid file type. Please upload an image.",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                400,
            )

        image_data = file.read()
        result = style_advisor.analyze_skin_tone(image_data)

        if not result["success"]:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": result["error"],
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                400,
            )

        return jsonify(
            {
                "success": True,
                "data": result["data"],
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Image analysis endpoint error: {e}")
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
            "services": {
                "price_prediction": prediction_service.model is not None,
                "style_advisor": style_advisor.gemini_configured,
            },
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/", methods=["GET"])
def home():
    return jsonify(
        {
            "message": "Fashion AI API",
            "version": "2.0.0",
            "endpoints": {
                "health": "/api/health (GET)",
                "occasions": "/api/occasions (GET)",
                "predict": "/api/predict (POST)",
                "style_recommendation": "/api/style-recommendation (POST)",
                "analyze_image": "/api/analyze-image (POST)",
            },
        }
    )


if __name__ == "__main__":
    logger.info("Starting Server...")
    app.run(debug=True, port=8000, host="0.0.0.0")
