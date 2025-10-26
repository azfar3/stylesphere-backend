import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()


class GeminiOccasionAnalyzer:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash")
        else:
            self.model = None
            print("Warning: No Gemini API key provided. Using fallback rules.")

    def get_occasion_insights(self, product_title, brand, category, occasion):
        fallback_rules = {
            "outfitters": {
                "eid_ul_fitr": (25, 40),
                "eid_ul_azha": (20, 35),
                "independence_day": (15, 30),
                "christmas": (10, 25),
                "pakistan_day": (10, 20),
                "winter_sale": (30, 50),
            },
            "cougar": {
                "eid_ul_fitr": (20, 35),
                "eid_ul_azha": (15, 30),
                "independence_day": (10, 25),
                "christmas": (5, 20),
                "pakistan_day": (8, 18),
                "winter_sale": (25, 45),
            },
            "gulahmed": {
                "eid_ul_fitr": (30, 50),
                "eid_ul_azha": (25, 45),
                "independence_day": (20, 35),
                "christmas": (15, 30),
                "pakistan_day": (15, 25),
                "winter_sale": (35, 60),
            },
            "one": {
                "eid_ul_fitr": (15, 30),
                "eid_ul_azha": (10, 25),
                "independence_day": (10, 20),
                "christmas": (5, 15),
                "pakistan_day": (5, 15),
                "winter_sale": (20, 40),
            },
            "engine": {
                "eid_ul_fitr": (20, 40),
                "eid_ul_azha": (15, 35),
                "independence_day": (15, 25),
                "christmas": (10, 20),
                "pakistan_day": (10, 20),
                "winter_sale": (25, 50),
            },
        }

        if not self.model:
            brand_rules = fallback_rules.get(
                brand.lower(), fallback_rules["outfitters"]
            )
            occasion_discount = brand_rules.get(occasion, (15, 30))
            return {
                "min_discount": occasion_discount[0],
                "max_discount": occasion_discount[1],
                "confidence": "medium",
                "reasoning": f"Fallback rules for {brand} during {occasion}",
            }

        prompt = f"""
        Analyze discount patterns for Pakistani fashion brands.
        
        Product: {product_title}
        Brand: {brand}
        Category: {category}
        Occasion: {occasion}
        
        Based on typical Pakistani retail patterns, what discount range (percentage) 
        would this product likely have during {occasion}?
        
        Consider:
        - Brand pricing strategy
        - Product category (clothing, accessories, etc.)
        - Occasion significance in Pakistan
        - Typical sale durations and intensities
        
        Return ONLY valid JSON format:
        {{
            "min_discount": 15,
            "max_discount": 35, 
            "confidence": "high/medium/low",
            "reasoning": "Brief explanation"
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1]

            insights = json.loads(response_text)
            return insights

        except Exception as e:
            print(f"Gemini API error: {e}. Using fallback rules.")
            brand_rules = fallback_rules.get(
                brand.lower(), fallback_rules["outfitters"]
            )
            occasion_discount = brand_rules.get(occasion, (15, 30))
            return {
                "min_discount": occasion_discount[0],
                "max_discount": occasion_discount[1],
                "confidence": "low",
                "reasoning": f"Error: {str(e)}",
            }
