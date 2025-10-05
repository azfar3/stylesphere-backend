const express = require('express');
const router = express.Router();
const priceComparisonController = require('../controllers/priceComparisonController');
const auth = require('../middleware/auth');

router.get('/search', priceComparisonController.searchProductsForComparison);
router.get('/:productId', priceComparisonController.getComparisonProducts);
router.get('/:productId/price-history', priceComparisonController.getPriceHistory);

module.exports = router;