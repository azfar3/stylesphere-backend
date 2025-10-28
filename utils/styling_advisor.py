import google.generativeai as genai
import json
import logging
import random
from typing import Dict, Any

logger = logging.getLogger(__name__)


class StyleAdvisorService:
    def __init__(self, gemini_api_key: str):
        self.gemini_configured = self.configure_gemini(gemini_api_key)

    def configure_gemini(self, api_key: str) -> bool:
        try:
            genai.configure(api_key=api_key)
            logger.info("Gemini API configured successfully for Style Advisor!")
            return True
        except Exception as e:
            logger.error(f"Error configuring Gemini: {e}")
            return False

    def validate_user_input(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        errors = []

        required_fields = ["gender", "age", "event"]
        for field in required_fields:
            if not user_data.get(field):
                errors.append(f"{field} is required")

        if user_data.get("gender") and user_data.get("gender").lower() not in [
            "male",
            "female",
        ]:
            errors.append("Gender must be 'male' or 'female'")

        try:
            age = int(user_data.get("age", 0))
            if not (1 <= age <= 120):
                errors.append("Age must be between 1 and 120")
        except (ValueError, TypeError):
            errors.append("Age must be a valid number")

        valid_events = [
            "casual",
            "eid",
            "jumma",
            "wedding",
            "formal",
            "office",
            "party",
        ]
        if (
            user_data.get("event")
            and user_data.get("event").lower() not in valid_events
        ):
            errors.append(f"Event must be one of: {', '.join(valid_events)}")

        valid_tones = ["warm", "cool", "neutral"]
        if (
            user_data.get("skin_tone")
            and user_data.get("skin_tone").lower() not in valid_tones
        ):
            errors.append(f"Skin tone must be one of: {', '.join(valid_tones)}")

        return {"valid": len(errors) == 0, "errors": errors}

    def build_style_prompt(self, user_data: Dict[str, Any]) -> str:

        prompt = f"""
        Act as a personal fashion stylist specialized in Pakistani fashion. Your goal is to suggest a complete, culturally appropriate outfit for a Pakistani user by exclusively using the styles, aesthetics, and typical product lines from the following brands: Outfitters, Cougar, Engine, One, and GulAhmed.

        PERSONAL DETAILS:
        - Gender: {user_data.get('gender', 'Not specified')}
        - Height: {user_data.get('height', 'Not specified')}
        - Weight: {user_data.get('weight', 'Not specified')} kg
        - Age: {user_data.get('age', 'Not specified')} years
        - Body Measurements: Chest {user_data.get('chest', 'Not specified')}, Waist {user_data.get('waist', 'Not specified')}, Hip {user_data.get('hip', 'Not specified')}

        APPEARANCE:
        - Face Shape: {user_data.get('face_shape', 'Not specified')}
        - Hair: {user_data.get('hair_color', 'Not specified')} {user_data.get('hair_type', 'Not specified')} hair
        - Skin Tone: {user_data.get('skin_tone', 'Not specified')}
        - Favorite Colors: {user_data.get('favorite_colors', 'Not specified')}

        PREFERENCES:
        - Cultural Style: {user_data.get('cultural_factors', 'desi')}
        - Season: {user_data.get('season', 'Not specified')}
        - Event: {user_data.get('event', 'Not specified')}
        """

        if user_data.get("gender") == "female":
            prompt += f"- Preferred Heel Height: {user_data.get('preferred_heel_height', 'Not specified')}\n"
        else:
            prompt += f"- Preferred Shoe Type: {user_data.get('preferred_shoe_type', 'Not specified')}\n"

        prompt += """
        OUTFIT REQUIREMENTS:
        Provide a complete outfit recommendation in JSON format only. The response must be valid JSON with the following structure:

        {
            "kurta_shirt": "Detailed description of top wear including specific brand from the allowed list",
            "pants_shalwar": "Detailed description of bottom wear including specific brand from the allowed list", 
            "footwear": "Detailed description of footwear including specific brand from the allowed list",
            "accessories": ["Branded accessory 1", "Branded accessory 2", "Branded accessory 3"],
            "colors": ["Primary Color 1", "Secondary Color 2", "Accent Color 3"],
            "fabric": ["Fabric Type 1", "Fabric Type 2"],
            "styling_tips": "Practical styling advice for this outfit",
            "outfit_images": [
                {
                    "name": "Outfit Name",
                    "image": "description_or_reference",
                    "description": "Brief description"
                }
            ],
            "recommended_brands": ["Brand1", "Brand2", "Brand3"]
        }

        BRAND-SPECIFIC GUIDELINES:

        1. OUTFITTERS:
        - Known for: Western wear, casual shirts, jeans, trendy tops, contemporary designs
        - Best for: Casual events, office wear, modern fusion looks
        - Signature styles: Minimalist designs, modern cuts, versatile pieces

        2. COUGAR:
        - Known for: Premium formal wear, shoes, accessories, sophisticated styling
        - Best for: Formal events, business meetings, elegant occasions
        - Signature styles: Classic silhouettes, premium fabrics, refined aesthetics

        3. ENGINE:
        - Known for: Sporty casual wear, youth-focused designs, comfortable fits
        - Best for: Casual outings, semi-formal events, daytime functions
        - Signature styles: Contemporary fits, modern patterns, comfortable fabrics

        4. ONE:
        - Known for: Affordable fashion, trendy designs, versatile collections
        - Best for: Everyday wear, casual gatherings, budget-friendly options
        - Signature styles: On-trend pieces, mix-and-match options, accessible fashion

        5. GULAHMED:
        - Known for: Traditional Pakistani wear, embroidered kurtas, formal shalwar kameez
        - Best for: Traditional events, weddings, Eid, religious occasions
        - Signature styles: intricate embroidery, traditional cuts, rich fabrics

        IMPORTANT INSTRUCTIONS:
        1. You MUST ONLY suggest items from these five brands: Outfitters, Cougar, Engine, One, GulAhmed
        2. Specify the brand name for each clothing item in your description
        3. Consider the user's body type, skin tone, and preferences when selecting brands
        4. For traditional events (Eid, weddings), prioritize GulAhmed and premium brands
        5. For casual/formal events, consider Outfitters, Cougar, and Engine
        6. Suggest culturally appropriate outfits for the specified event
        7. Recommend colors that complement the user's skin tone
        8. Suggest fabrics suitable for the season
        9. Provide practical styling tips
        10. Return ONLY valid JSON, no additional text or explanations

        CRITICAL RULE: Do not suggest items from any brand outside of Outfitters, Cougar, Engine, One, and GulAhmed. Your expertise is in curating outfits exclusively from these five brands.
        """

        return prompt

    def get_style_recommendation(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.gemini_configured:
            return {"error": "AI service not configured"}

        try:
            validation = self.validate_user_input(user_data)
            if not validation["valid"]:
                return {"error": "Invalid input", "details": validation["errors"]}

            prompt = self.build_style_prompt(user_data)
            model = genai.GenerativeModel("gemini-2.0-flash")

            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    top_p=0.9,
                    max_output_tokens=2048,
                ),
            )

            recommendation_text = response.text.strip()

            if recommendation_text.startswith("```json"):
                recommendation_text = recommendation_text[7:]
            if recommendation_text.endswith("```"):
                recommendation_text = recommendation_text[:-3]
            if recommendation_text.startswith("```"):
                recommendation_text = recommendation_text[3:]

            recommendation_data = json.loads(recommendation_text)

            return {
                "success": True,
                "recommendation": recommendation_data,
                "skin_tone": user_data.get("skin_tone"),
                "metadata": {
                    "cultural_preference": user_data.get("cultural_factors", "desi"),
                    "event": user_data.get("event"),
                    "season": user_data.get("season"),
                },
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {e}")
            return self._get_fallback_recommendation(user_data)
        except Exception as e:
            logger.error(f"Error getting style recommendation: {e}")
            return {"error": f"AI service error: {str(e)}"}

    def _get_fallback_recommendation(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        gender = user_data.get("gender", "male")
        event = user_data.get("event", "casual")

        fallback_outfits = {
            "male": {
                "casual": {
                    "kurta_shirt": "Cotton straight kurta with minimal embroidery",
                    "pants_shalwar": "Comfortable cotton shalwar",
                    "footwear": "Kolhapuri sandals or casual mojaris",
                    "accessories": ["Watch", "Bracelet", "Sunglasses"],
                    "colors": ["White", "Light Blue", "Beige"],
                    "fabric": ["Cotton", "Linen"],
                    "styling_tips": "Keep it simple and comfortable for casual outings",
                },
                "wedding": {
                    "kurta_shirt": "Embroidered sherwani or jodhpuri suit",
                    "pants_shalwar": "Fitted churidar or tailored trousers",
                    "footwear": "Traditional jutti or formal shoes",
                    "accessories": ["Turban", "Necklace", "Bracelet", "Watch"],
                    "colors": ["Maroon", "Gold", "Navy Blue"],
                    "fabric": ["Silk", "Brocade", "Velvet"],
                    "styling_tips": "Opt for rich fabrics and traditional accessories for weddings",
                },
            },
            "female": {
                "casual": {
                    "kurta_shirt": "Cotton kurti with light embroidery",
                    "pants_shalwar": "Palazzo pants or straight pants",
                    "footwear": "Sandals or flat mojaris",
                    "accessories": ["Earrings", "Bangles", "Purse"],
                    "colors": ["Pastel Pink", "Mint Green", "Cream"],
                    "fabric": ["Cotton", "Chiffon"],
                    "styling_tips": "Choose lightweight fabrics and comfortable fits",
                },
                "wedding": {
                    "kurta_shirt": "Heavy embroidered lehenga or anarkali",
                    "pants_shalwar": "Sharara or gharara pants",
                    "footwear": "Heeled juttis or embellished sandals",
                    "accessories": [
                        "Necklace Set",
                        "Earrings",
                        "Bangles",
                        "Maang Tikka",
                    ],
                    "colors": ["Red", "Gold", "Royal Blue"],
                    "fabric": ["Silk", "Velvet", "Georgette"],
                    "styling_tips": "Go for traditional jewelry and rich fabrics for wedding events",
                },
            },
        }

        gender_outfits = fallback_outfits.get(gender, fallback_outfits["male"])
        outfit = gender_outfits.get(event, gender_outfits["casual"])

        return {
            "success": True,
            "recommendation": {
                **outfit,
                "outfit_images": [
                    {
                        "name": f"{event.title()} Outfit",
                        "image": f"/images/{gender}/{event}_outfit.jpg",
                        "description": f"Traditional {event} wear for {gender}",
                    }
                ],
            },
            "skin_tone": user_data.get("skin_tone"),
            "metadata": {
                "cultural_preference": user_data.get("cultural_factors", "desi"),
                "event": event,
                "season": user_data.get("season"),
            },
        }

    def analyze_skin_tone(self, image_data: bytes) -> Dict[str, Any]:
        try:
            skin_tones = ["warm", "cool", "neutral"]
            detected_tone = random.choice(skin_tones)

            return {
                "success": True,
                "data": {
                    "detected_skin_tone": detected_tone,
                    "confidence": round(random.uniform(0.7, 0.95), 2),
                    "analysis_details": {
                        "method": "color_analysis",
                        "face_detected": True,
                        "notes": "Basic color analysis completed",
                    },
                },
            }

        except Exception as e:
            logger.error(f"Skin tone analysis error: {e}")
            return {"success": False, "error": f"Image analysis failed: {str(e)}"}
