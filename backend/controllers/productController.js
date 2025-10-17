import Product from '../models/Product.js';

export const getProducts = async (req, res) => {
    try {
        const {
            page = 1,
            limit = 12,
            category, search,
            brand, minPrice,
            maxPrice,
            sortBy = 'title',
            sortOrder = 'asc'
        } = req.query;

        let filter = { availability: { $ne: false } };
        if (category) {
            filter.category = { $regex: category, $options: 'i' };
        }
        if (brand) {
            filter.brand = { $regex: brand, $options: 'i' };
        }
        if (minPrice || maxPrice) {
            filter.price_clean = {};
            if (minPrice) filter.price_clean.$gte = Number(minPrice);
            if (maxPrice) filter.price_clean.$lte = Number(maxPrice);
        }
        if (search) {
            filter.$or = [
                { title: { $regex: search, $options: 'i' } },
                { brand: { $regex: search, $options: 'i' } },
                { style_type: { $regex: search, $options: 'i' } },
                { product_type: { $regex: search, $options: 'i' } }
            ];
        }

        const sortFieldMap = {
            'name': 'title',
            'price': 'price_clean',
            'rating': 'rating',
            'createdAt': 'createdAt'
        };

        const sort = {};
        const actualSortField = sortFieldMap[sortBy] || sortBy;
        sort[actualSortField] = sortOrder === 'desc' ? -1 : 1;

        const skip = (parseInt(page) - 1) * parseInt(limit);

        const products = await Product.find(filter)
            .sort(sort)
            .skip(skip)
            .limit(parseInt(limit))

        const total = await Product.countDocuments(filter);
        const totalPages = Math.ceil(total / parseInt(limit));

        res.status(200).json({
            success: true,
            data: products,
            pagination: {
                page: parseInt(page),
                limit: parseInt(limit),
                total,
                totalPages,
                hasNextPage: page < totalPages,
                hasPrevPage: page > 1
            }
        });
    } catch (error) {
        console.error('Error fetching products:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to fetch products',
            error: process.env.NODE_ENV === 'development' ? error.message : 'Internal server error'
        });
    }
};

export const getProductById = async (req, res) => {
    try {
        const { id } = req.params;

        if (!id) {
            return res.status(400).json({
                success: false,
                message: 'Product ID is required'
            });
        }

        let product = await Product.findOne({ product_id: id });
        if (!product) {
            product = await Product.findById(id);
        }

        if (!product) {
            return res.status(404).json({
                success: false,
                message: 'Product not found'
            });
        }

        res.status(200).json({
            success: true,
            data: product
        });
    } catch (error) {
        console.error('Error fetching product by ID:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to fetch product',
            error: process.env.NODE_ENV === 'development' ? error.message : 'Internal server error'
        });
    }
};

export const searchProducts = async (req, res) => {
    try {
        const { q, category, minPrice, maxPrice, brand, tags } = req.query;

        if (!q && !category && !brand && !tags && !minPrice && !maxPrice) {
            return res.status(400).json({
                success: false,
                message: 'Search query, category, brand, or tags required'
            });
        }

        let filter = { availability: { $ne: false } };

        if (q) {
            filter.$or = [
                { title: { $regex: q, $options: 'i' } },
                { brand: { $regex: q, $options: 'i' } },
                { style_type: { $regex: q, $options: 'i' } },
                { product_type: { $regex: q, $options: 'i' } }
            ];
        }

        if (category) {
            filter.category = { $regex: category, $options: 'i' };
        }

        if (brand) {
            filter.brand = { $regex: brand, $options: 'i' };
        }

        if (minPrice || maxPrice) {
            filter.price_clean = {};
            if (minPrice) filter.price_clean.$gte = parseFloat(minPrice);
            if (maxPrice) filter.price_clean.$lte = parseFloat(maxPrice);
        }

        const products = await Product.find(filter)
            .sort({ title: 1 })
            .limit(50)

        res.status(200).json({
            success: true,
            data: products,
            count: products.length
        });
    } catch (error) {
        console.error('Error searching products:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to search products',
            error: process.env.NODE_ENV === 'development' ? error.message : 'Internal server error'
        });
    }
};

export const getFeaturedProducts = async (req, res) => {
    try {
        const limit = parseInt(req.query.limit) || 8;

        const products = await Product.find({
            availability: true,
            is_discounted: true
        })
            .sort({ discount_clean: -1, createdAt: -1 })
            .limit(limit)

        res.status(200).json({
            success: true,
            count: products.length,
            data: products
        });
    } catch (error) {
        console.error('Error fetching featured products:', error);
        res.status(500).json({
            success: false,
            error: 'Server Error - Unable to fetch featured products'
        });
    }
};

export const getTopDiscounts = async (req, res) => {
    try {
        const products = await Product.find({
            discount_clean: { $gt: 0 },
            availability: true
        })
            .sort({ discount_clean: -1 })
            .limit(10);

        res.json({ success: true, data: products });
    } catch (error) {
        res.status(500).json({ success: false, message: error.message });
    }
};

export const createProduct = async (req, res) => {
    try {
        const product = new Product(req.body);
        const savedProduct = await product.save();
        res.status(201).json(savedProduct);
    } catch (error) {
        res.status(400).json({ message: error.message });
    }
};