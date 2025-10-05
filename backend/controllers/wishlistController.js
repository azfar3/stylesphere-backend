import User from '../models/User.js';
import Product from '../models/Product.js';

export const getWishlist = async (req, res) => {
    try {
        const user = await User.findById(req.user.id).populate('wishlist');
        if (!user) {
            return res.status(404).json({ success: false, message: 'User not found' });
        }
        res.json({ success: true, data: user.wishlist });
    } catch (err) {
        res.status(500).json({ success: false, message: 'Failed to fetch wishlist' });
    }
};

export const addToWishlist = async (req, res) => {
    try {
        const { productId } = req.body;

        const user = await User.findById(req.user.id);
        if (!user) return res.status(404).json({ success: false, message: 'User not found' });

        const product = await Product.findById(productId);
        if (!product) return res.status(404).json({ success: false, message: 'Product not found' });

        if (user.wishlist.includes(productId)) {
            return res.status(400).json({ success: false, message: 'Already in wishlist' });
        }

        user.wishlist.push(productId);
        await user.save();

        const updatedUser = await user.populate('wishlist');
        res.json({ success: true, message: 'Added to wishlist', data: updatedUser.wishlist });
    } catch (err) {
        res.status(500).json({ success: false, message: err.message });
    }
};


export const removeFromWishlist = async (req, res) => {
    try {
        const { productId } = req.params;

        const user = await User.findById(req.user.id);
        if (!user) return res.status(404).json({ success: false, message: 'User not found' });

        user.wishlist = user.wishlist.filter(id => id.toString() !== productId);
        await user.save();

        const updatedUser = await user.populate('wishlist');
        res.json({ success: true, message: 'Removed from wishlist', data: updatedUser.wishlist });
    } catch (err) {
        res.status(500).json({ success: false, message: 'Failed to remove product' });
    }
};

export const toggleTracking = async (req, res) => {
    try {
        const { productId } = req.params;
        const user = await User.findById(req.user.id);

        if (!user) {
            return res.status(404).json({ success: false, message: 'User not found' });
        }

        // Check if product is in wishlist before allowing tracking
        if (!user.wishlist.includes(productId)) {
            return res.status(400).json({
                success: false,
                message: 'Product must be in wishlist to track'
            });
        }

        const trackingIndex = user.trackingEnabled.indexOf(productId);

        if (trackingIndex > -1) {
            // Remove from tracking
            user.trackingEnabled.splice(trackingIndex, 1);
            await user.save();
            res.json({
                success: true,
                message: 'Tracking disabled',
                tracking: false
            });
        } else {
            // Add to tracking
            user.trackingEnabled.push(productId);
            await user.save();
            res.json({
                success: true,
                message: 'Tracking enabled',
                tracking: true
            });
        }
    } catch (err) {
        res.status(500).json({
            success: false,
            message: 'Failed to update tracking'
        });
    }
};