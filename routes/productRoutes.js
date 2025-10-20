import express from 'express';
import { getProducts, getProductById, searchProducts, getFeaturedProducts, createProduct, getTopDiscounts } from '../controllers/productController.js';
const router = express.Router();

router.post('/', createProduct);
router.get('/search', searchProducts);
router.get('/featured', getFeaturedProducts);
router.get('/', getProducts);
router.get("/top-discounts", getTopDiscounts);
router.get('/:id', getProductById);

export default router;
