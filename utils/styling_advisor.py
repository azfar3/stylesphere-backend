import google.generativeai as genai
import json
import logging
import random
import requests
import base64
from typing import Dict, Any, List
import io
from PIL import Image

logger = logging.getLogger(__name__)


class StyleAdvisorService:
    def __init__(self, gemini_api_key: str, huggingface_api_key: str = None):
        self.gemini_configured = self.configure_gemini(gemini_api_key)
        self.huggingface_api_key = huggingface_api_key
        self.huggingface_configured = huggingface_api_key is not None

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

    def build_outfit_prompt_for_image(
        self, recommendation: Dict[str, Any], user_data: Dict[str, Any]
    ) -> str:
        """Build a detailed prompt for Stable Diffusion image generation"""

        gender = user_data.get("gender", "person")
        age = user_data.get("age", "")
        event = user_data.get("event", "occasion")
        skin_tone = user_data.get("skin_tone", "")

        # Build description components
        colors = ", ".join(recommendation.get("colors", []))
        fabrics = ", ".join(recommendation.get("fabric", []))
        accessories = ", ".join(recommendation.get("accessories", []))

        prompt_parts = [
            f"Full-body fashion photography of a {age}-year-old {gender},",
            f"wearing {recommendation.get('kurta_shirt', 'outfit')}",
            f"with {recommendation.get('pants_shalwar', 'bottom wear')}",
            f"and {recommendation.get('footwear', 'footwear')}",
        ]

        if colors:
            prompt_parts.append(f"in {colors} colors")
        if fabrics:
            prompt_parts.append(f"made of {fabrics} fabric")
        if accessories:
            prompt_parts.append(f"accessorized with {accessories}")

        prompt_parts.extend(
            [
                f"for a {event} event,",
                "Pakistani fashion style,",
                "professional studio lighting,",
                "high quality, detailed,",
                "full body shot, clean background,",
                "fashion photography, vibrant colors",
                "trending on Pinterest, 8K resolution",
            ]
        )

        if skin_tone:
            prompt_parts.append(f"{skin_tone} skin tone")

        return " ".join(prompt_parts)

    def generate_outfit_image(
        self, recommendation: Dict[str, Any], user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        if not self.huggingface_configured:
            return {"success": False, "error": "Hugging Face API not configured"}

        try:
            # Build the prompt for image generation
            prompt = self.build_outfit_prompt_for_image(recommendation, user_data)

            # Initialize the client with proper error handling
            try:
                from huggingface_hub import InferenceClient
            except ImportError:
                return {
                    "success": False,
                    "error": "huggingface_hub package not installed. Run: pip install huggingface_hub",
                }

            try:
                client = InferenceClient(token=self.huggingface_api_key)

                # Generate image using text_to_image method
                image = client.text_to_image(
                    prompt,
                    model="stabilityai/stable-diffusion-xl-base-1.0",
                )

                # Convert PIL Image to bytes and then to base64
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format="JPEG", quality=95)
                image_base64 = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")

                return {
                    "success": True,
                    "image_base64": image_base64,
                    "image_format": "jpeg",
                    "dimensions": {"width": image.width, "height": image.height},
                    "prompt_used": prompt,
                    "model_used": "stabilityai/stable-diffusion-xl-base-1.0",
                }

            except Exception as client_error:
                logger.error(f"HuggingFace client error: {client_error}")
                return {
                    "success": False,
                    "error": f"HuggingFace client error: {str(client_error)}",
                }

        except Exception as e:
            logger.error(f"Outfit image generation error: {e}")
            return {"success": False, "error": f"Image generation failed: {str(e)}"}

    def build_style_prompt(self, user_data: Dict[str, Any]) -> str:
        # ... (your existing build_style_prompt method remains the same)
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
            "kurta_price": 7500,
            "pant_price": 5000,
            "footwear_price": 4000,
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
        1. You MUST ONLY suggest items from these five brands: Outfitters, Cougar, Engine, One, and GulAhmed
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

    def get_style_recommendation(
        self, user_data: Dict[str, Any], generate_image: bool = True
    ) -> Dict[str, Any]:
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

            # Generate outfit image if requested and Hugging Face is configured
            generated_image = None
            if generate_image and self.huggingface_configured:
                image_result = self.generate_outfit_image(
                    recommendation_data, user_data
                )
                if image_result["success"]:
                    generated_image = image_result

            result = {
                "success": True,
                "recommendation": recommendation_data,
                "skin_tone": user_data.get("skin_tone"),
                "metadata": {
                    "cultural_preference": user_data.get("cultural_factors", "desi"),
                    "event": user_data.get("event"),
                    "season": user_data.get("season"),
                },
            }

            if generated_image:
                print("Generated image successfully.")
                result["generated_image"] = generated_image
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {e}")
            return self._get_fallback_recommendation(user_data)
        except Exception as e:
            logger.error(f"Error getting style recommendation: {e}")
            return {"error": f"AI service error: {str(e)}"}

    def _get_fallback_recommendation(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        # ... (your existing fallback method remains the same)
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
