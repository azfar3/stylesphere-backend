#!/usr/bin/env python3
"""
Style Advisor Engine
Converts the styling.ipynb notebook into a standalone Python script
for backend integration with Node.js
"""

import os
import sys
import json
import argparse
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import warnings

# Suppress sklearn warnings
warnings.filterwarnings("ignore")

STYLING_SERVICE_AVAILABLE = True

class StyleAdvisor:
    def __init__(self, api_endpoint=None, api_token=None):
        self.api_endpoint = api_endpoint
        self.api_token = api_token
        self.cultural_styles = {
            'desi': {
                'male': {
                    'formal': ['Kurta with waistcoat', 'Sherwani', 'Formal shalwar kameez'],
                    'casual': ['Cotton kurta', 'Casual shalwar', 'T-shirt with jeans'],
                    'wedding': ['Sherwani with churidar', 'Heavy embroidered kurta', 'Traditional waistcoat'],
                    'eid': ['Silk kurta', 'Embroidered shalwar kameez', 'Designer kurta'],
                    'jumma': ['Simple kurta', 'White shalwar kameez', 'Cotton kurta']
                },
                'female': {
                    'formal': ['Formal shalwar kameez', 'Business suit', 'Elegant kurta with trousers'],
                    'casual': ['Cotton shalwar kameez', 'Kurti with jeans', 'Simple dupatta set'],
                    'wedding': ['Heavy lehenga', 'Bridal sharara', 'Designer anarkali'],
                    'eid': ['Silk shalwar kameez', 'Embroidered suit', 'Festive dupatta set'],
                    'jumma': ['Simple shalwar kameez', 'Modest dupatta set', 'Cotton suit']
                }
            },
            'western': {
                'male': {
                    'formal': ['Business suit', 'Blazer with trousers', 'Formal shirt and tie'],
                    'casual': ['Jeans with t-shirt', 'Polo shirt', 'Casual chinos'],
                    'party': ['Party blazer', 'Dress shirt', 'Stylish jeans']
                },
                'female': {
                    'formal': ['Business suit', 'Formal dress', 'Blazer with skirt'],
                    'casual': ['Jeans with top', 'Casual dress', 'Blouse with trousers'],
                    'party': ['Cocktail dress', 'Party top with skirt', 'Elegant jumpsuit']
                }
            }
        }
        
        self.color_palettes = {
            'warm': {
                'primary': ['Gold', 'Orange', 'Red', 'Yellow', 'Peach', 'Coral'],
                'secondary': ['Brown', 'Olive Green', 'Rust', 'Maroon', 'Cream'],
                'neutral': ['Cream', 'Warm White', 'Beige', 'Camel', 'Tan'],
                'avoid': ['Cool Blue', 'Purple', 'Cool Pink', 'Silver']
            },
            'cool': {
                'primary': ['Blue', 'Purple', 'Cool Pink', 'Silver', 'Turquoise'],
                'secondary': ['Navy', 'Teal', 'Emerald Green', 'Cool Red', 'Mint'],
                'neutral': ['Pure White', 'Cool Grey', 'Black', 'Charcoal'],
                'avoid': ['Orange', 'Gold', 'Warm Yellow', 'Coral']
            },
            'neutral': {
                'primary': ['All colors work well', 'Earth tones', 'Jewel tones'],
                'secondary': ['Pastels', 'Bold colors', 'Classic colors'],
                'neutral': ['White', 'Grey', 'Beige', 'Black', 'Navy'],
                'avoid': ['Very bright neons only in small amounts']
            }
        }
        
        self.fabric_suggestions = {
            'summer': ['Cotton', 'Lawn', 'Chiffon', 'Georgette', 'Linen'],
            'winter': ['Wool', 'Cashmere', 'Velvet', 'Heavy silk', 'Khaddar'],
            'spring': ['Cotton', 'Silk', 'Light wool', 'Chiffon'],
            'fall': ['Cotton blend', 'Light wool', 'Denim', 'Corduroy']
        }

    def extract_dominant_color(self, image_path):
        """Extract dominant color from uploaded image for skin tone detection"""
        try:
            image = Image.open(image_path).resize((150, 150))
            img_data = np.array(image).reshape((-1, 3))
            kmeans = KMeans(n_clusters=1, random_state=42, n_init=10).fit(img_data)
            dominant_color = kmeans.cluster_centers_[0].astype(int)
            return tuple(dominant_color)
        except Exception as e:
            print(f"Error reading image: {e}", file=sys.stderr)
            return None

    def classify_skin_tone(self, rgb):
        """Classify skin tone based on RGB values"""
        if not rgb:
            return "neutral"
            
        r, g, b = rgb
        # Simple classification based on color temperature
        if r > g and r > b and (r - b) > 10:
            return "warm"
        elif b > r and b > g and (b - r) > 10:
            return "cool"
        else:
            return "neutral"

    def get_body_type_recommendations(self, measurements):
        """Provide recommendations based on body measurements"""
        try:
            chest = float(str(measurements.get('chest', '0')).replace('inches', '').replace('cm', '').strip())
            waist = float(str(measurements.get('waist', '0')).replace('inches', '').replace('cm', '').strip())
            hip = float(str(measurements.get('hip', '0')).replace('inches', '').replace('cm', '').strip())
        except (ValueError, AttributeError):
            return "Choose fitted clothing that flatters your body shape"

        if chest and waist and hip:
            if waist < chest and waist < hip:
                return "A-line silhouettes work well for you. Consider fitted tops and flowy bottoms."
            elif chest > waist > hip:
                return "Balance your proportions with fitted bottoms and structured tops."
            else:
                return "You can wear most styles! Focus on clothes that make you feel confident."
        
        return "Choose well-fitted clothing that complements your body shape"

    def _get_outfit_images(self, gender, event, cultural_factors):
        """Generate image suggestions for outfits"""
        # Base outfit image suggestions with high-quality, relevant images
        outfit_images = {
            'desi': {
                'male': {
                    'casual': [
                        {'name': 'Cotton Kurta with Jeans', 'image': 'https://images.unsplash.com/photo-1506794778202-cad84cf45f82?w=400&h=500&fit=crop', 'description': 'Modern casual look combining traditional kurta with jeans'},
                        {'name': 'Simple Shalwar Kameez', 'image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=500&fit=crop', 'description': 'Classic traditional casual wear for daily comfort'},
                        {'name': 'Polo Shirt with Chinos', 'image': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=500&fit=crop', 'description': 'Smart casual western style'},
                    ],
                    'formal': [
                        {'name': 'Formal Kurta with Waistcoat', 'image': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=500&fit=crop', 'description': 'Professional formal traditional attire'},
                        {'name': 'Business Shalwar Kameez', 'image': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=500&fit=crop', 'description': 'Traditional formal wear for office'},
                        {'name': 'Suit with Tie', 'image': 'https://images.unsplash.com/photo-1594824883131-e7db2609d5a6?w=400&h=500&fit=crop', 'description': 'Classic business suit'},
                    ],
                    'wedding': [
                        {'name': 'Embroidered Sherwani', 'image': 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&h=500&fit=crop', 'description': 'Elegant wedding sherwani with intricate embroidery'},
                        {'name': 'Heavy Kurta with Churidar', 'image': 'https://images.unsplash.com/photo-1542206395-9feb3edaa68d?w=400&h=500&fit=crop', 'description': 'Festive wedding attire with traditional pants'},
                        {'name': 'Designer Waistcoat Set', 'image': 'https://images.unsplash.com/photo-1617137984095-74e4e5e3613f?w=400&h=500&fit=crop', 'description': 'Luxurious three-piece wedding outfit'},
                    ],
                    'eid': [
                        {'name': 'Silk Kurta', 'image': 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=400&h=500&fit=crop', 'description': 'Premium silk kurta for Eid celebrations'},
                        {'name': 'Embroidered Shalwar Kameez', 'image': 'https://images.unsplash.com/photo-1605722243252-3b9c74127781?w=400&h=500&fit=crop', 'description': 'Festive embroidered outfit'},
                    ],
                    'party': [
                        {'name': 'Designer Kurta', 'image': 'https://images.unsplash.com/photo-1617137984095-74e4e5e3613f?w=400&h=500&fit=crop', 'description': 'Stylish party kurta'},
                        {'name': 'Blazer with Jeans', 'image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=500&fit=crop', 'description': 'Smart casual party look'},
                    ],
                },
                'female': {
                    'casual': [
                        {'name': 'Cotton Shalwar Kameez', 'image': 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=500&fit=crop', 'description': 'Comfortable daily wear in breathable cotton'},
                        {'name': 'Kurti with Jeans', 'image': 'https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=400&h=500&fit=crop', 'description': 'Modern fusion style mixing traditional and western'},
                        {'name': 'Palazzo Set', 'image': 'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=400&h=500&fit=crop', 'description': 'Trendy palazzo pants with matching top'},
                    ],
                    'formal': [
                        {'name': 'Elegant Shalwar Kameez', 'image': 'https://images.unsplash.com/photo-1494790108755-2616c6c1f8b5?w=400&h=500&fit=crop', 'description': 'Professional formal wear for office'},
                        {'name': 'Business Suit Style', 'image': 'https://images.unsplash.com/photo-1557804506-669a67965ba0?w=400&h=500&fit=crop', 'description': 'Contemporary office attire'},
                        {'name': 'Formal Shirt Dress', 'image': 'https://images.unsplash.com/photo-1594824883131-e7db2609d5a6?w=400&h=500&fit=crop', 'description': 'Professional western-style dress'},
                    ],
                    'wedding': [
                        {'name': 'Bridal Lehenga', 'image': 'https://images.unsplash.com/photo-1551024506-0bccd828d307?w=400&h=500&fit=crop', 'description': 'Traditional bridal wear with intricate work'},
                        {'name': 'Designer Anarkali', 'image': 'https://images.unsplash.com/photo-1551024601-bec78aea704b?w=400&h=500&fit=crop', 'description': 'Festive wedding outfit with flowing silhouette'},
                        {'name': 'Sharara Set', 'image': 'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=400&h=500&fit=crop', 'description': 'Elegant sharara for wedding functions'},
                    ],
                    'eid': [
                        {'name': 'Silk Shalwar Kameez', 'image': 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=500&fit=crop', 'description': 'Luxurious silk outfit for Eid'},
                        {'name': 'Embroidered Suit', 'image': 'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=400&h=500&fit=crop', 'description': 'Festive embroidered three-piece'},
                    ],
                    'party': [
                        {'name': 'Designer Kurti Set', 'image': 'https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=400&h=500&fit=crop', 'description': 'Stylish party kurti with pants'},
                        {'name': 'Western Dress', 'image': 'https://images.unsplash.com/photo-1551024601-bec78aea704b?w=400&h=500&fit=crop', 'description': 'Elegant western party dress'},
                    ],
                }
            },
            'western': {
                'male': {
                    'casual': [
                        {'name': 'Jeans with T-shirt', 'image': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=500&fit=crop', 'description': 'Classic casual western look'},
                        {'name': 'Polo Shirt', 'image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=500&fit=crop', 'description': 'Smart casual polo style'},
                    ],
                    'formal': [
                        {'name': 'Business Suit', 'image': 'https://images.unsplash.com/photo-1594824883131-e7db2609d5a6?w=400&h=500&fit=crop', 'description': 'Professional business attire'},
                        {'name': 'Blazer with Trousers', 'image': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=500&fit=crop', 'description': 'Semi-formal blazer combination'},
                    ],
                    'party': [
                        {'name': 'Dress Shirt', 'image': 'https://images.unsplash.com/photo-1617137984095-74e4e5e3613f?w=400&h=500&fit=crop', 'description': 'Stylish dress shirt for parties'},
                        {'name': 'Smart Casual Blazer', 'image': 'https://images.unsplash.com/photo-1542206395-9feb3edaa68d?w=400&h=500&fit=crop', 'description': 'Perfect blazer for social events'},
                    ],
                },
                'female': {
                    'casual': [
                        {'name': 'Jeans with Top', 'image': 'https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=400&h=500&fit=crop', 'description': 'Comfortable casual western wear'},
                        {'name': 'Casual Dress', 'image': 'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=400&h=500&fit=crop', 'description': 'Easy-going dress for daily wear'},
                    ],
                    'formal': [
                        {'name': 'Business Suit', 'image': 'https://images.unsplash.com/photo-1557804506-669a67965ba0?w=400&h=500&fit=crop', 'description': 'Professional suit for office'},
                        {'name': 'Formal Dress', 'image': 'https://images.unsplash.com/photo-1494790108755-2616c6c1f8b5?w=400&h=500&fit=crop', 'description': 'Elegant formal dress'},
                    ],
                    'party': [
                        {'name': 'Cocktail Dress', 'image': 'https://images.unsplash.com/photo-1551024601-bec78aea704b?w=400&h=500&fit=crop', 'description': 'Stunning cocktail dress'},
                        {'name': 'Elegant Jumpsuit', 'image': 'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=400&h=500&fit=crop', 'description': 'Modern jumpsuit for parties'},
                    ],
                }
            },
            'fusion': {
                'male': {
                    'casual': [
                        {'name': 'Kurta with Jeans', 'image': 'https://images.unsplash.com/photo-1506794778202-cad84cf45f82?w=400&h=500&fit=crop', 'description': 'Perfect fusion of traditional and modern'},
                        {'name': 'Designer T-shirt', 'image': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=500&fit=crop', 'description': 'Contemporary casual wear'},
                    ],
                    'formal': [
                        {'name': 'Nehru Jacket Set', 'image': 'https://images.unsplash.com/photo-1617137984095-74e4e5e3613f?w=400&h=500&fit=crop', 'description': 'Indo-western formal look'},
                        {'name': 'Blazer with Kurta', 'image': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=500&fit=crop', 'description': 'Fusion formal attire'},
                    ],
                },
                'female': {
                    'casual': [
                        {'name': 'Indo-Western Top', 'image': 'https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=400&h=500&fit=crop', 'description': 'Modern fusion casual wear'},
                        {'name': 'Ethnic Jacket with Jeans', 'image': 'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=400&h=500&fit=crop', 'description': 'Trendy ethnic jacket styling'},
                    ],
                    'formal': [
                        {'name': 'Fusion Dress', 'image': 'https://images.unsplash.com/photo-1551024601-bec78aea704b?w=400&h=500&fit=crop', 'description': 'Indo-western formal dress'},
                        {'name': 'Palazzo with Blazer', 'image': 'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=400&h=500&fit=crop', 'description': 'Professional fusion look'},
                    ],
                }
            }
        }
        
        try:
            return outfit_images.get(cultural_factors, {}).get(gender, {}).get(event, [])
        except:
            return []

    def get_style_recommendation(self, user_data, image_path=None):
        """Generate comprehensive outfit recommendation"""
        gender = user_data.get('gender', 'male').lower()
        event = user_data.get('event', 'casual').lower()
        cultural_factors = user_data.get('cultural_factors', 'desi').lower()
        season = user_data.get('season', 'current').lower()
        skin_tone = user_data.get('skin_tone', 'neutral').lower()
        favorite_colors = user_data.get('favorite_colors', '').lower().split(',') if user_data.get('favorite_colors') else []
        
        # Handle skin tone detection if image is provided
        detected_skin_tone = None
        if image_path and os.path.exists(image_path):
            dominant_color = self.extract_dominant_color(image_path)
            detected_skin_tone = self.classify_skin_tone(dominant_color)
            skin_tone = detected_skin_tone
        
        # Get base outfit suggestions
        style_category = self.cultural_styles.get(cultural_factors, self.cultural_styles['desi'])
        gender_styles = style_category.get(gender, style_category['male'])
        
        if event in gender_styles:
            base_suggestions = gender_styles[event]
        else:
            base_suggestions = gender_styles.get('casual', ['Basic outfit recommended'])

        # Get color recommendations
        color_palette = self.color_palettes.get(skin_tone, self.color_palettes['neutral'])
        
        # Get fabric recommendations
        fabric_suggestions = self.fabric_suggestions.get(season, self.fabric_suggestions['summer'])
        
        # Get outfit images
        outfit_images = self._get_outfit_images(gender, event, cultural_factors)
        
        # Generate comprehensive recommendation
        recommendation = {
            'kurta_shirt': base_suggestions[0] if base_suggestions else 'Fitted kurta or shirt',
            'pants_shalwar': 'Matching shalwar or fitted trousers',
            'footwear': self._get_footwear_recommendation(gender, event, user_data),
            'accessories': self._get_accessories_recommendation(gender, event, cultural_factors),
            'colors': self._get_personalized_colors(color_palette, favorite_colors),
            'fabric': fabric_suggestions[:3],  # Top 3 fabric suggestions
            'styling_tips': self._get_styling_tips(user_data),
            'outfit_images': outfit_images  # Add image suggestions
        }
        
        return {
            'success': True,
            'recommendation': recommendation,
            'skin_tone': skin_tone,
            'source': 'ai_styling_engine'
        }

    def _get_footwear_recommendation(self, gender, event, user_data):
        """Get footwear recommendations"""
        preferred_type = user_data.get('preferred_shoe_type', '').lower()
        preferred_heel = user_data.get('preferred_heel_height', '').lower()
        
        if gender == 'female':
            if 'flat' in preferred_heel:
                return "Flat khussa, ballet flats, or comfortable sandals"
            else:
                return "Low heel pumps, block heels, or elegant sandals"
        else:
            if 'boot' in preferred_type:
                return "Leather boots, Chelsea boots, or dress boots"
            elif 'sandal' in preferred_type:
                return "Leather sandals, chappals, or kolhapuri"
            else:
                return "Formal shoes, loafers, or oxford shoes"

    def _get_accessories_recommendation(self, gender, event, cultural_factors):
        """Get accessories recommendations"""
        if cultural_factors == 'desi':
            if gender == 'female':
                return ['Dupatta', 'Traditional jewelry', 'Bangles', 'Small earrings']
            else:
                return ['Watch', 'Cufflinks', 'Pocket square', 'Traditional cap (optional)']
        else:
            if gender == 'female':
                return ['Statement jewelry', 'Watch', 'Handbag', 'Scarf (optional)']
            else:
                return ['Watch', 'Belt', 'Tie/bow tie', 'Cufflinks']

    def _get_personalized_colors(self, color_palette, favorite_colors):
        """Get personalized color recommendations"""
        recommended = color_palette['primary'][:3]
        
        # If user has favorite colors, try to include compatible ones
        if favorite_colors:
            for fav_color in favorite_colors:
                fav_color = fav_color.strip()
                if fav_color and fav_color not in color_palette['avoid']:
                    if fav_color not in recommended:
                        recommended.append(fav_color)
        
        return recommended[:5]  # Return top 5 color recommendations

    def _get_styling_tips(self, user_data):
        """Generate personalized styling tips"""
        tips = []
        
        # Body measurements based tips
        body_tip = self.get_body_type_recommendations(user_data)
        tips.append(body_tip)
        
        # Season based tips
        season = user_data.get('season', '').lower()
        if season == 'summer':
            tips.append("Choose breathable fabrics and lighter colors to stay cool.")
        elif season == 'winter':
            tips.append("Layer wisely and choose warm fabrics like wool or cashmere.")
        
        # Event based tips
        event = user_data.get('event', '').lower()
        if event == 'wedding':
            tips.append("Don't be afraid to go bold with colors and embellishments.")
        elif event == 'formal':
            tips.append("Keep it classic and well-tailored for a professional look.")
        
        return " ".join(tips) if tips else "Choose clothes that make you feel confident and comfortable!"

# Fallback recommendations
FALLBACK_RECOMMENDATIONS = {
    "casual": {
        "male": {
            "kurta_shirt": "Cotton casual shirt or simple kurta in light colors",
            "pants_shalwar": "Jeans or casual trousers",
            "footwear": "Sneakers or casual shoes",
            "accessories": ["Watch", "Simple chain"],
            "colors": ["Blue", "White", "Black", "Grey"],
            "fabric": ["Cotton", "Denim"]
        },
        "female": {
            "kurta_shirt": "Cotton kurti or casual top",
            "pants_shalwar": "Jeans or straight pants", 
            "footwear": "Flats or casual sandals",
            "accessories": ["Simple jewelry", "Handbag"],
            "colors": ["Pastels", "White", "Black", "Navy"],
            "fabric": ["Cotton", "Lawn", "Chiffon"]
        }
    },
    "formal": {
        "male": {
            "kurta_shirt": "Formal kurta or dress shirt",
            "pants_shalwar": "Formal trousers or dress shalwar",
            "footwear": "Leather shoes or formal khussas",
            "accessories": ["Watch", "Cufflinks", "Waistcoat"],
            "colors": ["White", "Cream", "Navy", "Black"],
            "fabric": ["Cotton", "Silk", "Khaddar"]
        },
        "female": {
            "kurta_shirt": "Elegant kurti or formal top",
            "pants_shalwar": "Formal trousers or palazzo",
            "footwear": "Heels or formal flats", 
            "accessories": ["Statement jewelry", "Clutch", "Dupatta"],
            "colors": ["Rich jewel tones", "Gold", "Silver", "Deep colors"],
            "fabric": ["Silk", "Chiffon", "Organza"]
        }
    }
}

def get_fallback_recommendation(user_data):
    """Generate fallback recommendation when AI service is not available"""
    gender = user_data.get('gender', 'male').lower()
    event = user_data.get('event', 'casual').lower()
    
    # Map events to categories
    if event in ['wedding', 'formal', 'office']:
        category = 'formal'
    else:
        category = 'casual'
    
    if gender not in ['male', 'female']:
        gender = 'male'
    
    if category not in FALLBACK_RECOMMENDATIONS:
        category = 'casual'
    
    base_rec = FALLBACK_RECOMMENDATIONS[category][gender].copy()
    
    # Customize based on user preferences
    if user_data.get('favorite_colors'):
        user_colors = [c.strip() for c in user_data['favorite_colors'].split(',')]
        base_rec['colors'] = user_colors + base_rec['colors'][:2]  # Keep some defaults
    
    base_rec['styling_tips'] = f"Perfect for {event} occasions. Choose comfortable fabrics for the {user_data.get('season', 'current')} season."
    
    return {
        "success": True,
        "recommendation": base_rec,
        "skin_tone": user_data.get('skin_tone', 'neutral'),
        "user_preferences": user_data,
        "source": "fallback_recommendations"
    }

def main():
    try:
        # Read input from stdin (from Node.js)
        input_data = sys.stdin.read()
        if not input_data.strip():
            print(json.dumps({"error": "No input data provided"}))
            return
        
        # Parse input JSON
        data = json.loads(input_data)
        user_data = data.get('user_data', {})
        image_path = data.get('image_path')
        
        # Use Style Advisor if available
        if STYLING_SERVICE_AVAILABLE:
            try:
                advisor = StyleAdvisor(
                    api_endpoint=os.getenv('AZURE_ENDPOINT'),
                    api_token=os.getenv('AZURE_API_KEY')
                )
                result = advisor.get_style_recommendation(user_data, image_path)
            except Exception as e:
                print(json.dumps({"warning": f"AI service failed: {str(e)}, using fallback"}), file=sys.stderr)
                result = get_fallback_recommendation(user_data)
        else:
            result = get_fallback_recommendation(user_data)
        
        # Output result as JSON
        print(json.dumps(result, indent=2))
        
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON input: {str(e)}"}))
    except Exception as e:
        print(json.dumps({"error": f"Service error: {str(e)}"}))

if __name__ == "__main__":
    main()
