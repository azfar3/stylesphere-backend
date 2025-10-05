#!/usr/bin/env python3
"""
Price Prediction Service for StyleSphere
Placeholder for ML model - to be integrated with your price prediction model
"""

import sys
import json
import os
from datetime import datetime, timedelta
import random
import math

class PricePredictionService:
    def __init__(self):
        """Initialize the price prediction service"""
        self.model_version = "1.0.0-placeholder"
        print(f"Price Prediction Service initialized (v{self.model_version})")
    
    def generate_historical_data(self, base_price, days=30):
        """Generate mock historical price data"""
        historical_data = []
        current_date = datetime.now() - timedelta(days=days)
        current_price = base_price
        
        for i in range(days):
            # Add some realistic price fluctuation
            change_percent = random.uniform(-0.05, 0.05)  # ±5% daily change
            current_price = max(0.01, current_price * (1 + change_percent))
            
            historical_data.append({
                "date": current_date.isoformat(),
                "price": round(current_price, 2)
            })
            current_date += timedelta(days=1)
        
        return historical_data
    
    def analyze_price_factors(self, product_data):
        """Analyze factors affecting price prediction"""
        factors = []
        
        # Category-based factors
        category = product_data.get('category', '').lower()
        if 'fashion' in category or 'clothing' in category:
            factors.append({
                "factor": "Seasonal Demand",
                "impact": "positive" if datetime.now().month in [11, 12, 3, 4] else "neutral",
                "weight": 0.3
            })
            factors.append({
                "factor": "Fashion Trends",
                "impact": random.choice(["positive", "negative", "neutral"]),
                "weight": 0.25
            })
        
        # Brand-based factors
        brand = product_data.get('brand', '').lower()
        if any(luxury in brand for luxury in ['gucci', 'prada', 'louis', 'chanel']):
            factors.append({
                "factor": "Luxury Brand Premium",
                "impact": "positive",
                "weight": 0.4
            })
        
        # Price range factors
        price = product_data.get('price', 0)
        if price > 1000:
            factors.append({
                "factor": "High-End Market Stability",
                "impact": "neutral",
                "weight": 0.2
            })
        elif price < 100:
            factors.append({
                "factor": "Budget Market Volatility",
                "impact": "negative",
                "weight": 0.15
            })
        
        # Add default factors if none found
        if not factors:
            factors = [
                {
                    "factor": "Market Competition",
                    "impact": "negative",
                    "weight": 0.3
                },
                {
                    "factor": "Supply Chain Stability",
                    "impact": "neutral",
                    "weight": 0.2
                }
            ]
        
        return factors
    
    def predict_price_trend(self, historical_data, target_days):
        """Predict price trend based on historical data"""
        if len(historical_data) < 7:
            return "stable"
        
        # Analyze recent trend (last 7 days)
        recent_prices = [item['price'] for item in historical_data[-7:]]
        
        if recent_prices[-1] > recent_prices[0] * 1.05:
            return "increasing"
        elif recent_prices[-1] < recent_prices[0] * 0.95:
            return "decreasing"
        else:
            return "stable"
    
    def calculate_prediction_confidence(self, factors, historical_data):
        """Calculate confidence level for prediction"""
        base_confidence = 75
        
        # Adjust based on data quality
        if len(historical_data) > 30:
            base_confidence += 10
        elif len(historical_data) < 7:
            base_confidence -= 20
        
        # Adjust based on factors certainty
        high_impact_factors = [f for f in factors if f['weight'] > 0.3]
        if len(high_impact_factors) > 0:
            base_confidence += 5
        
        # Add some randomness for realism
        confidence = base_confidence + random.randint(-10, 10)
        return max(20, min(95, confidence))  # Keep between 20-95%
    
    def predict_price(self, product_data, target_days=30):
        """
        Main price prediction function
        
        Args:
            product_data: Dictionary containing product information
            target_days: Number of days in future to predict
            
        Returns:
            Dictionary containing prediction results
        """
        try:
            current_price = product_data.get('price', 100)
            
            # Generate historical data (this would come from your database in production)
            historical_data = self.generate_historical_data(current_price)
            
            # Analyze factors affecting price
            factors = self.analyze_price_factors(product_data)
            
            # Calculate predicted price with some realistic variation
            base_change = random.uniform(-0.15, 0.15)  # ±15% base change
            
            # Apply factor impacts
            factor_impact = 0
            for factor in factors:
                impact_value = 0.05 if factor['impact'] == 'positive' else (-0.05 if factor['impact'] == 'negative' else 0)
                factor_impact += impact_value * factor['weight']
            
            total_change = base_change + factor_impact
            predicted_price = current_price * (1 + total_change)
            predicted_price = max(current_price * 0.5, predicted_price)  # Don't go below 50% of current price
            
            # Determine trend
            trend = self.predict_price_trend(historical_data, target_days)
            
            # Calculate confidence
            confidence = self.calculate_prediction_confidence(factors, historical_data)
            
            target_date = (datetime.now() + timedelta(days=target_days)).isoformat()
            
            return {
                "success": True,
                "prediction": {
                    "current_price": round(current_price, 2),
                    "predicted_price": round(predicted_price, 2),
                    "target_date": target_date,
                    "confidence": confidence,
                    "trend": trend,
                    "price_change_percent": round(((predicted_price - current_price) / current_price) * 100, 2),
                    "factors": factors,
                    "historical_data": historical_data[-10:],  # Last 10 days only
                    "recommendation": self.get_recommendation(current_price, predicted_price, trend, confidence)
                },
                "metadata": {
                    "model_version": self.model_version,
                    "prediction_date": datetime.now().isoformat(),
                    "target_days": target_days
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_prediction": {
                    "current_price": product_data.get('price', 100),
                    "predicted_price": product_data.get('price', 100),
                    "confidence": 50,
                    "trend": "stable",
                    "recommendation": "Monitor price regularly for changes"
                }
            }
    
    def get_recommendation(self, current_price, predicted_price, trend, confidence):
        """Generate buying recommendation based on prediction"""
        price_change = ((predicted_price - current_price) / current_price) * 100
        
        if confidence < 60:
            return "Monitor price closely due to low prediction confidence"
        
        if price_change < -10:
            return "Consider waiting - price may drop significantly"
        elif price_change > 10:
            return "Consider buying now - price likely to increase"
        elif trend == "increasing" and price_change > 5:
            return "Buy soon - upward trend detected"
        elif trend == "decreasing" and price_change < -5:
            return "Wait a bit longer - price may continue to drop"
        else:
            return "Price is relatively stable - good time to buy if needed"

def main():
    """Command line interface for testing"""
    try:
        # Read input from stdin
        input_data = sys.stdin.read()
        if not input_data.strip():
            print(json.dumps({"error": "No input data provided"}))
            return
        
        data = json.loads(input_data)
        product_data = data.get('product_data', {})
        target_days = data.get('target_days', 30)
        
        # Initialize service and make prediction
        service = PricePredictionService()
        result = service.predict_price(product_data, target_days)
        
        print(json.dumps(result, indent=2))
        
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON input: {str(e)}"}))
    except Exception as e:
        print(json.dumps({"error": f"Service error: {str(e)}"}))

if __name__ == "__main__":
    main()
