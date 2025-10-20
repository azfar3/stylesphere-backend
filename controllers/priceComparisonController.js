import Product from '../models/Product.js';
import Comparison from '../models/Comparison.js';

export const compareMultipleProducts = async (req, res) => {
    try {
        const { products: productIds } = req.body;

        if (!productIds || !Array.isArray(productIds) || productIds.length === 0) {
            return res.status(400).json({
                success: false,
                message: 'Product IDs array is required'
            });
        }

        if (productIds.length > 5) {
            return res.status(400).json({
                success: false,
                message: 'You can compare up to 5 products at a time'
            });
        }

        const products = await Product.find({
            $or: [
                { _id: { $in: productIds } },
                { product_id: { $in: productIds } }
            ]
        });

        if (products.length === 0) {
            return res.status(404).json({
                success: false,
                message: 'No products found for comparison'
            });
        }

        const comparisonData = products.map(product => ({
            id: product._id || product.product_id,
            product_id: product.product_id,
            name: product.title,
            brand: product.brand,
            category: product.category,
            price: product.price,
            originalPrice: product.originalPrice,
            discount: product.discount,
            image: product.image,
            rating: product.rating,
            description: product.description,
            productType: product.product_type,
            fitType: product.fit_type,
            materialType: product.material_type,
            primaryColor: product.primary_color,
            sizeVariant: product.size_variant,
            styleType: product.style_type,
            inStock: product.inStock,
            stockQuantity: product.stockQuantity
        }));

        if (req.user) {
            await Comparison.create({
                userId: req.user.id,
                productIds: productIds,
                comparisonData: comparisonData,
                comparedAt: new Date()
            });
        }

        res.status(200).json({
            success: true,
            data: comparisonData,
            count: comparisonData.length
        });

    } catch (error) {
        console.error('Error comparing products:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to compare products',
            error: process.env.NODE_ENV === 'development' ? error.message : 'Internal server error'
        });
    }
};

export const getComparisonHistory = async (req, res) => {
    try {
        const comparisons = await Comparison.find({ userId: req.user.id })
            .sort({ comparedAt: -1 })
            .limit(10)
            .populate('productIds');

        res.status(200).json({
            success: true,
            data: comparisons
        });
    } catch (error) {
        console.error('Error fetching comparison history:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to fetch comparison history'
        });
    }
};

export const saveComparison = async (req, res) => {
    try {
        const { products: productIds, name } = req.body;

        const savedComparison = await Comparison.create({
            userId: req.user.id,
            productIds: productIds,
            name: name || `Comparison ${new Date().toLocaleDateString()}`,
            savedAt: new Date(),
            isSaved: true
        });

        res.status(201).json({
            success: true,
            data: savedComparison,
            message: 'Comparison saved successfully'
        });
    } catch (error) {
        console.error('Error saving comparison:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to save comparison'
        });
    }
};