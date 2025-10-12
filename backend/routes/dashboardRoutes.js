import express from 'express';
import { protect } from '../middleware/authMiddleware.js';
import {
    getDashboardOverview,
    getPriceAnalytics,
    getStyleRecommendations,
    getSpendingAnalytics
} from '../controllers/dashboardController.js';

const router = express.Router();

router.get('/dashboard/overview', protect, getDashboardOverview);
router.get('/dashboard/price-analytics', protect, getPriceAnalytics);
router.get('/dashboard/recommendations', protect, getStyleRecommendations);
router.get('/dashboard/spending-analytics', protect, getSpendingAnalytics);

export default router;