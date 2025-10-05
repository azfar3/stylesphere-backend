import express from 'express';
import {
  getTrackedProducts,
  getActivePredictions,
  addToTracker,
  removeFromTracker,
  getPricePrediction,
  updatePredictionAccuracy
} from '../controllers/trackerController.js';
import { protect } from '../middleware/authMiddleware.js';
import { body, param, query } from 'express-validator';
import { handleValidationErrors } from '../middleware/validationMiddleware.js';

const router = express.Router();

// Validation middleware
const validateAddToTracker = [
  body('productId')
    .isMongoId()
    .withMessage('Invalid product ID'),
  body('targetDays')
    .optional()
    .isInt({ min: 1, max: 365 })
    .withMessage('Target days must be between 1 and 365'),
  handleValidationErrors
];

const validateProductId = [
  param('productId')
    .isMongoId()
    .withMessage('Invalid product ID'),
  handleValidationErrors
];

const validatePredictionId = [
  param('predictionId')
    .isMongoId()
    .withMessage('Invalid prediction ID'),
  body('actualPrice')
    .isFloat({ min: 0 })
    .withMessage('Actual price must be a positive number'),
  handleValidationErrors
];

const validateTargetDays = [
  query('targetDays')
    .optional()
    .isInt({ min: 1, max: 365 })
    .withMessage('Target days must be between 1 and 365'),
  handleValidationErrors
];

// Routes

// Get all tracked products for user
router.get('/', protect, getTrackedProducts);

// Get active price predictions
router.get('/active', protect, getActivePredictions);

// Add product to tracker with price prediction
router.post('/add', protect, validateAddToTracker, addToTracker);

// Remove product from tracker
router.delete('/:productId', protect, validateProductId, removeFromTracker);

// Get price prediction for specific product (without adding to tracker)
router.get('/predict/:productId', protect, validateProductId, validateTargetDays, getPricePrediction);

// Update prediction accuracy
router.put('/prediction/:predictionId/accuracy', protect, validatePredictionId, updatePredictionAccuracy);

export default router;
