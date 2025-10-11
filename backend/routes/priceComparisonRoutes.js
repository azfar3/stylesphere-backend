import express from 'express';
import { getComparisonData, getPriceTrends } from '../controllers/priceComparisonController.js';

const router = express.Router();

router.get('/', getComparisonData);
router.get('/trends/:productId', getPriceTrends);

export default router;