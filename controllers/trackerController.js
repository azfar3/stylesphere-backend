import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import Tracker from '../models/Tracker.js';
import Product from '../models/Product.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const executeMLPricePrediction = (productData, targetDays = 30) => {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(__dirname, '../utils/ml_price_service.py');

    const inputData = JSON.stringify({
      product_data: productData,
      target_days: targetDays
    });

    const pythonProcess = spawn('python', [pythonScript], {
      stdio: ['pipe', 'pipe', 'pipe']
    });

    let output = '';
    let errorOutput = '';

    pythonProcess.stdout.on('data', (data) => {
      output += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        console.error('ML service error:', errorOutput);
        return reject(new Error(`ML prediction service error: ${errorOutput}`));
      }

      try {
        const result = JSON.parse(output);
        resolve(result);
      } catch (parseError) {
        console.error('Failed to parse ML output:', output);
        reject(new Error('Invalid response from ML service'));
      }
    });

    pythonProcess.on('error', (error) => {
      console.error('Failed to start ML service:', error);
      reject(new Error('Failed to start ML prediction service'));
    });

    pythonProcess.stdin.write(inputData);
    pythonProcess.stdin.end();
  });
};

export const getTrackingStatus = async (req, res) => {
  try {
    const { productId } = req.params;

    const track = await Tracker.findOne({
      user: req.user.id,
      product: productId,
      isActive: true
    });

    res.json({
      success: true,
      data: {
        isTracking: !!track,
        mlInsights: track?.mlInsights || null
      }
    });
  } catch (error) {
    console.error('Get tracking status error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error'
    });
  }
};

export const addToTracker = async (req, res) => {
  try {
    const { productId, targetDays = 30 } = req.body;

    const product = await Product.findById(productId);
    if (!product) {
      return res.status(404).json({
        success: false,
        message: 'Product not found'
      });
    }

    const existingTrack = await Tracker.findOne({
      user: req.user.id,
      product: productId,
      isActive: true
    });

    if (existingTrack) {
      return res.status(400).json({
        success: false,
        message: 'Already tracking this product'
      });
    }

    const productData = {
      id: product._id.toString(),
      name: product.name,
      price: product.price,
      originalPrice: product.originalPrice || product.price * 1.2,
      discount: product.discount || 0,
      category: product.category,
      brand: product.brand,
      description: product.description || '',
      images: product.images || []
    };

    let mlPrediction;
    try {
      mlPrediction = await executeMLPricePrediction(productData, targetDays);

      if (!mlPrediction.success) {
        console.warn('ML prediction failed, using fallback');
        throw new Error('ML prediction failed');
      }

      console.log('ML Prediction received:', {
        current: mlPrediction.prediction.current_price,
        predicted: mlPrediction.prediction.predicted_price,
        confidence: mlPrediction.prediction.confidence,
        trend: mlPrediction.prediction.trend,
        change: mlPrediction.prediction.price_change_percent + '%'
      });

    } catch (mlError) {
      console.warn('ML service error, using fallback:', mlError.message);
      mlPrediction = {
        success: true,
        prediction: {
          current_price: product.price,
          predicted_price: product.price * 0.95,
          confidence: 60,
          trend: 'stable',
          price_change_percent: -5,
          factors: [{ factor: 'Fallback', impact: 'neutral', weight: 1.0 }],
          recommendation: 'Conservative estimate - monitor prices'
        },
        metadata: { model_type: 'fallback' }
      };
    }

    const track = new Tracker({
      user: req.user.id,
      product: productId,
      productName: product.name,
      currentPrice: product.price,
      image: product.images?.[0] || product.image,
      isActive: true,
      mlInsights: {
        predictedPrice: mlPrediction.prediction.predicted_price,
        confidence: mlPrediction.prediction.confidence,
        trend: mlPrediction.prediction.trend,
        priceChangePercent: mlPrediction.prediction.price_change_percent,
        recommendation: mlPrediction.prediction.recommendation,
        factors: mlPrediction.prediction.factors,
        modelType: mlPrediction.metadata?.model_type || 'fallback',
        lastPrediction: new Date()
      }
    });

    await track.save();

    res.status(201).json({
      success: true,
      message: 'Price tracking started with ML insights',
      data: {
        track,
        prediction: mlPrediction.prediction,
        metadata: mlPrediction.metadata
      }
    });

  } catch (error) {
    console.error('Add to tracker error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error'
    });
  }
};

export const removeFromTracker = async (req, res) => {
  try {
    const { productId } = req.params;

    const track = await Tracker.findOneAndUpdate(
      {
        user: req.user.id,
        product: productId
      },
      { isActive: false },
      { new: true }
    );

    if (!track) {
      return res.status(404).json({
        success: false,
        message: 'Tracking not found'
      });
    }

    res.json({
      success: true,
      message: 'Price tracking stopped'
    });
  } catch (error) {
    console.error('Remove from tracker error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error'
    });
  }
};

export const getTrackedProducts = async (req, res) => {
  try {
    const tracks = await Tracker.find({
      user: req.user.id,
      isActive: true
    })
      .populate('product', 'name price images category brand discount originalPrice')
      .sort({ createdAt: -1 });

    res.json({
      success: true,
      data: tracks
    });
  } catch (error) {
    console.error('Get tracked products error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error'
    });
  }
};

export const getPricePrediction = async (req, res) => {
  try {
    const { productId } = req.params;
    const { targetDays = 30 } = req.query;

    const product = await Product.findById(productId);
    if (!product) {
      return res.status(404).json({
        success: false,
        message: 'Product not found'
      });
    }

    const productData = {
      id: product._id.toString(),
      name: product.name,
      price: product.price,
      originalPrice: product.originalPrice || product.price * 1.2,
      discount: product.discount || 0,
      category: product.category,
      brand: product.brand,
      description: product.description || ''
    };

    const prediction = await executeMLPricePrediction(productData, parseInt(targetDays));

    res.json({
      success: true,
      data: {
        product: {
          id: product._id,
          name: product.name,
          price: product.price,
          image: product.images?.[0],
          category: product.category,
          brand: product.brand
        },
        prediction: prediction.prediction,
        metadata: prediction.metadata
      }
    });

  } catch (error) {
    console.error('Get price prediction error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to get price prediction'
    });
  }
};

export const getActivePredictions = async (req, res) => {
  try {
    const tracks = await Tracker.find({
      user: req.user.id,
      isActive: true
    })
      .populate('product', 'name price images category brand')
      .sort({ createdAt: -1 });

    res.json({
      success: true,
      data: {
        predictions: tracks,
        count: tracks.length
      }
    });
  } catch (error) {
    console.error('Get active predictions error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error'
    });
  }
};

export const updatePredictionAccuracy = async (req, res) => {
  try {
    const { predictionId } = req.params;
    const { actualPrice } = req.body;

    const track = await Tracker.findById(predictionId);

    if (!track) {
      return res.status(404).json({
        success: false,
        error: 'Prediction not found'
      });
    }

    const predictedPrice = track.mlInsights?.predictedPrice || track.currentPrice;
    const accuracy = Math.max(0, 100 - Math.abs(((actualPrice - predictedPrice) / predictedPrice) * 100));

    track.mlInsights.accuracy = accuracy;
    await track.save();

    res.json({
      success: true,
      message: 'Prediction accuracy updated',
      data: {
        accuracy: Math.round(accuracy),
        predictedPrice: predictedPrice,
        actualPrice: actualPrice
      }
    });

  } catch (error) {
    console.error('Update prediction accuracy error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error'
    });
  }
};