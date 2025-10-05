const Product = require('../models/Product');
const PriceHistory = require('../models/PriceHistory');

const priceComparisonController = {
    // Get similar products for comparison
    getComparisonProducts: async (req, res) => {
        try {
            const { productId } = req.params;
            const { category, brand, priceRange, limit = 10 } = req.query;

            // Get main product details
            const mainProduct = await Product.findById(productId);
            if (!mainProduct) {
                return res.status(404).json({
                    success: false,
                    message: 'Product not found'
                });
            }

            // Build query for similar products
            const query = {
                _id: { $ne: productId }, // Exclude the main product
                category: mainProduct.category
            };

            // Add optional filters
            if (brand) query.brand = brand;
            if (priceRange) {
                const [minPrice, maxPrice] = priceRange.split('-').map(Number);
                query.price = { $gte: minPrice, $lte: maxPrice };
            }

            // Get similar products
            const similarProducts = await Product.find(query)
                .limit(parseInt(limit))
                .sort({ price: 1 }); // Sort by price ascending

            res.json({
                success: true,
                data: {
                    mainProduct,
                    similarProducts,
                    comparisonCount: similarProducts.length
                }
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                message: error.message
            });
        }
    },

    // Search products for comparison
    searchProductsForComparison: async (req, res) => {
        try {
            const { search, category, minPrice, maxPrice, sortBy = 'price', sortOrder = 'asc' } = req.query;

            let query = {};

            // Text search
            if (search) {
                query.$or = [
                    { name: { $regex: search, $options: 'i' } },
                    { brand: { $regex: search, $options: 'i' } },
                    { description: { $regex: search, $options: 'i' } }
                ];
            }

            // Category filter
            if (category) {
                query.category = category;
            }

            // Price range filter
            if (minPrice || maxPrice) {
                query.price = {};
                if (minPrice) query.price.$gte = Number(minPrice);
                if (maxPrice) query.price.$lte = Number(maxPrice);
            }

            const sortOptions = {};
            sortOptions[sortBy] = sortOrder === 'desc' ? -1 : 1;

            const products = await Product.find(query)
                .sort(sortOptions)
                .limit(50);

            res.json({
                success: true,
                data: products,
                total: products.length
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                message: error.message
            });
        }
    },

    // Get price history
    getPriceHistory: async (req, res) => {
        try {
            const { productId } = req.params;

            const priceHistory = await PriceHistory.find({ productId })
                .sort({ date: -1 })
                .limit(30); // Last 30 days

            res.json({
                success: true,
                data: priceHistory
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                message: error.message
            });
        }
    }
};

module.exports = priceComparisonController;