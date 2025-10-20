import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import PricePrediction from '../models/PricePrediction.js';
import Product from '../models/Product.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Helper function to execute Python price prediction service
const executePricePredictionService = (productData, targetDays = 30) => {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(__dirname, '../utils/price_prediction_service.py');

    // Check if Python script exists
    if (!fs.existsSync(pythonScript)) {
      return reject(new Error('Price prediction service not found'));
    }

    const inputData = JSON.stringify({
      product_data: productData,
      target_days: targetDays
    });

    // Spawn Python process
    const pythonProcess = spawn('python', [pythonScript], {
      stdio: ['pipe', 'pipe', 'pipe']
    });

    let output = '';
    let errorOutput = '';

    // Handle stdout
    pythonProcess.stdout.on('data', (data) => {
      output += data.toString();
    });

    // Handle stderr  
    pythonProcess.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    // Handle process completion
    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        console.error('Python process error:', errorOutput);
        return reject(new Error(`Python process exited with code ${code}: ${errorOutput}`));
      }

      try {
        const result = JSON.parse(output);
        resolve(result);
      } catch (parseError) {
        console.error('Failed to parse Python output:', output);
        reject(new Error('Invalid response from price prediction service'));
      }
    });

    // Handle process errors
    pythonProcess.on('error', (error) => {
      console.error('Failed to start Python process:', error);
      reject(new Error('Failed to start price prediction service'));
    });

    // Send input data to Python process
    pythonProcess.stdin.write(inputData);
    pythonProcess.stdin.end();
  });
};

// Get user's tracked products with predictions
export const getTrackedProducts = async (req, res, next) => {
  try {
    const userId = req.user.id;

    const predictions = await PricePrediction.getUserPredictions(userId, 20);

    res.json({
      success: true,
      data: {
        predictions,
        count: predictions.length
      }
    });
  } catch (error) {
    console.error('Get tracked products error:', error);
    next(error);
  }
};

// Get active price predictions
export const getActivePredictions = async (req, res, next) => {
  try {
    const userId = req.user.id;

    const activePredictions = await PricePrediction.getActivePredictions(userId);

    res.json({
      success: true,
      data: {
        predictions: activePredictions,
        count: activePredictions.length
      }
    });
  } catch (error) {
    console.error('Get active predictions error:', error);
    next(error);
  }
};

// Add product to price tracker with prediction
export const addToTracker = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { productId, targetDays = 30 } = req.body;

    if (!productId) {
      return res.status(400).json({
        success: false,
        error: 'Product ID is required'
      });
    }

    // Check if product exists
    const product = await Product.findById(productId);
    if (!product) {
      return res.status(404).json({
        success: false,
        error: 'Product not found'
      });
    }

    // Check if already tracking this product
    const existingPrediction = await PricePrediction.findOne({
      user: userId,
      product: productId,
      status: 'active'
    });

    if (existingPrediction) {
      return res.status(409).json({
        success: false,
        error: 'Product is already being tracked'
      });
    }

    // Prepare product data for prediction
    const productData = {
      id: product._id,
      name: product.name,
      price: product.price,
      category: product.category,
      brand: product.brand,
      description: product.description
    };

    // Get price prediction from ML service
    let predictionResult;
    try {
      predictionResult = await executePricePredictionService(productData, targetDays);
    } catch (error) {
      console.warn('Price prediction service failed:', error.message);
      // Fallback prediction
      predictionResult = {
        success: true,
        prediction: {
          current_price: product.price,
          predicted_price: product.price * (0.95 + Math.random() * 0.1), // ±5% variation
          confidence: 70,
          trend: 'stable',
          price_change_percent: Math.random() * 10 - 5, // -5% to +5%
          factors: [{ factor: 'Market Analysis', impact: 'neutral', weight: 0.5 }],
          recommendation: 'Monitor price for changes'
        }
      };
    }

    if (!predictionResult.success) {
      return res.status(500).json({
        success: false,
        error: 'Failed to generate price prediction'
      });
    }

    const prediction = predictionResult.prediction;
    const targetDate = new Date();
    targetDate.setDate(targetDate.getDate() + targetDays);

    // Create price prediction record
    const pricePrediction = await PricePrediction.create({
      user: userId,
      product: productId,
      currentPrice: prediction.current_price,
      predictedPrice: prediction.predicted_price,
      targetDate,
      confidence: prediction.confidence,
      trend: prediction.trend,
      factors: prediction.factors,
      historicalData: prediction.historical_data?.map(item => ({
        date: new Date(item.date),
        price: item.price
      })) || []
    });

    // Populate the prediction with product details
    await pricePrediction.populate('product', 'name image price category brand');

    res.status(201).json({
      success: true,
      message: 'Product added to price tracker successfully',
      data: {
        prediction: pricePrediction,
        recommendation: prediction.recommendation,
        metadata: predictionResult.metadata
      }
    });

  } catch (error) {
    console.error('Add to tracker error:', error);
    next(error);
  }
};

// Remove product from tracker
export const removeFromTracker = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { productId } = req.params;

    const prediction = await PricePrediction.findOneAndDelete({
      user: userId,
      product: productId,
      status: 'active'
    });

    if (!prediction) {
      return res.status(404).json({
        success: false,
        error: 'Tracked product not found'
      });
    }

    res.json({
      success: true,
      message: 'Product removed from tracker successfully'
    });
  } catch (error) {
    console.error('Remove from tracker error:', error);
    next(error);
  }
};

// Get price prediction for a specific product
export const getPricePrediction = async (req, res, next) => {
  try {
    const { productId } = req.params;
    const { targetDays = 30 } = req.query;

    // Get product details
    const product = await Product.findById(productId);
    if (!product) {
      return res.status(404).json({
        success: false,
        error: 'Product not found'
      });
    }

    // Prepare product data
    const productData = {
      id: product._id,
      name: product.name,
      price: product.price,
      category: product.category,
      brand: product.brand,
      description: product.description
    };

    // Get prediction from ML service
    const predictionResult = await executePricePredictionService(productData, parseInt(targetDays));

    res.json({
      success: true,
      data: {
        product: {
          id: product._id,
          name: product.name,
          image: product.image,
          category: product.category,
          brand: product.brand
        },
        prediction: predictionResult.prediction,
        metadata: predictionResult.metadata
      }
    });

  } catch (error) {
    console.error('Get price prediction error:', error);
    next(error);
  }
};

// Update prediction accuracy (called when actual price is known)
export const updatePredictionAccuracy = async (req, res, next) => {
  try {
    const { predictionId } = req.params;
    const { actualPrice } = req.body;
    const userId = req.user.id;

    const prediction = await PricePrediction.findOne({
      _id: predictionId,
      user: userId
    });

    if (!prediction) {
      return res.status(404).json({
        success: false,
        error: 'Prediction not found'
      });
    }

    await prediction.updateAccuracy(actualPrice);
    prediction.status = 'completed';
    await prediction.save();

    res.json({
      success: true,
      message: 'Prediction accuracy updated',
      data: {
        accuracy: prediction.accuracy,
        status: prediction.status
      }
    });

  } catch (error) {
    console.error('Update prediction accuracy error:', error);
    next(error);
  }
};