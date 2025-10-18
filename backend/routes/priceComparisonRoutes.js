import express from 'express';
import {
    getComparisonData,
    getPriceTrends,
    getProductTypes,
} from '../controllers/priceComparisonController.js';

const router = express.Router();

router.get('/', getComparisonData);
router.get('/trends/:productId', getPriceTrends);
router.get('/product-types', getProductTypes);

export default router;