import express from 'express';
import { getWishlist, addToWishlist, removeFromWishlist, toggleTracking } from '../controllers/wishlistController.js';
import protect from '../middleware/authMiddleware.js';
const router = express.Router();

router.get('/', protect, getWishlist);
router.post('/', protect, addToWishlist);
router.delete('/:productId', protect, removeFromWishlist);
router.patch('/:productId/track', protect, toggleTracking);

export default router;