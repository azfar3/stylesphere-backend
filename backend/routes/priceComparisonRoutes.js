import express from 'express';
import {
    compareMultipleProducts,
    getComparisonHistory,
    saveComparison
} from '../controllers/priceComparisonController.js';
import { protect } from '../middleware/authMiddleware.js';

const router = express.Router();

router.post('/compare-multiple', protect, compareMultipleProducts);
router.get('/history', protect, getComparisonHistory);
router.post('/save', protect, saveComparison);

export default router;