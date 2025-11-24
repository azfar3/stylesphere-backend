import express from 'express';
import {
  getTrackedProducts,
  getActivePredictions,
  addToTracker,
  removeFromTracker,
  getPricePrediction,
  updatePredictionAccuracy,
  getTrackingStatus
} from '../controllers/trackerController.js';
import { protect } from '../middleware/authMiddleware.js';

const router = express.Router();

router.get('/', protect, getTrackedProducts);
router.get('/active', protect, getActivePredictions);
router.get('/status/:productId', protect, getTrackingStatus);
router.post('/track', protect, addToTracker);
router.delete('/stop/:productId', protect, removeFromTracker);
router.get('/predict/:productId', protect, getPricePrediction);
router.put('/prediction/:predictionId/accuracy', protect, updatePredictionAccuracy);

export default router;