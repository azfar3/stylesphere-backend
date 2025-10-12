import User from '../models/User.js';
import Wishlist from '../models/Wishlist.js';

export const getDashboardOverview = async (req, res) => {
    try {
        const userId = req.user.id;

        console.log('Fetching dashboard data for user:', userId);

        const [wishlist, user] = await Promise.all([
            Wishlist.findOne({ user: userId }).populate('products'),
            User.findById(userId).select('name email createdAt avatar')
        ]);

        console.log('Fetched data:', {
            wishlist: wishlist?.products?.length,
            user: user?.name
        });

        const wishlistCount = wishlist?.products?.length || 0;
        const cartCount = 0;
        const orderCount = 0;
        const totalSpent = 0;

        const dashboardData = {
            user: {
                name: user?.name || req.user.name,
                email: user?.email || req.user.email,
                avatar: user?.avatar,
                memberSince: user?.createdAt || new Date(),
                membershipTier: calculateMembershipTier(totalSpent)
            },
            wishlistCount,
            cartCount,
            orderCount,
            totalSpent,
            styleMatch: calculateStyleMatch(wishlist),
            recentOrders: [],
            wishlistItems: (wishlist?.products?.slice(0, 4) || []).map(product => ({
                _id: product._id,
                name: product.name,
                price: product.price,
                quantity: product.quantity || 0,
                images: product.images || []
            })),
            styleSuggestions: generateStyleSuggestions(wishlist),
            priceAlerts: generatePriceAlerts(wishlist),
            quickStats: {
                totalProductsViewed: Math.floor(Math.random() * 50) + 10,
                favoriteCategory: getFavoriteCategory(wishlist),
                totalSavings: 0
            }
        };

        res.json({
            success: true,
            data: dashboardData
        });
    } catch (error) {
        console.error('Dashboard overview error:', error);
        res.status(500).json({
            success: false,
            message: 'Error fetching dashboard data',
            error: error.message
        });
    }
};

export const getPriceAnalytics = async (req, res) => {
    try {
        const userId = req.user.id;

        const wishlist = await Wishlist.findOne({ user: userId }).populate('products');
        const priceAnalytics = {
            totalTracked: wishlist?.products?.length || 0,
            priceDrops: Math.floor(Math.random() * 5),
            potentialSavings: Math.floor(Math.random() * 200) + 50,
            trend: 'stable'
        };

        res.json({
            success: true,
            data: priceAnalytics
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            message: 'Error fetching price analytics',
            error: error.message
        });
    }
};

export const getStyleRecommendations = async (req, res) => {
    try {
        const userId = req.user.id;

        const recommendations = [
            {
                id: 1,
                title: "Summer Casual Collection",
                description: "Based on your recent likes",
                image: "/images/summer-casual.jpg",
                confidence: 85,
                items: 12
            },
            {
                id: 2,
                title: "Minimalist Office Wear",
                description: "Matches your style profile",
                image: "/images/office-wear.jpg",
                confidence: 78,
                items: 8
            }
        ];

        res.json({
            success: true,
            data: recommendations
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            message: 'Error fetching recommendations',
            error: error.message
        });
    }
};

export const getSpendingAnalytics = async (req, res) => {
    try {
        const userId = req.user.id;

        const monthlySpending = Array.from({ length: 6 }, (_, i) => {
            const date = new Date();
            date.setMonth(date.getMonth() - i);
            return {
                month: date.toLocaleString('default', { month: 'short' }),
                amount: Math.floor(Math.random() * 500) + 100
            };
        }).reverse();

        const categorySpending = [
            { category: 'Clothing', amount: 450, color: '#1890ff' },
            { category: 'Accessories', amount: 200, color: '#52c41a' },
            { category: 'Footwear', amount: 300, color: '#faad14' },
            { category: 'Others', amount: 150, color: '#f5222d' }
        ];

        res.json({
            success: true,
            data: {
                monthlySpending,
                categorySpending,
                totalSpent: categorySpending.reduce((sum, item) => sum + item.amount, 0),
                averageOrder: 0
            }
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            message: 'Error fetching spending analytics',
            error: error.message
        });
    }
};

function calculateMembershipTier(totalSpent) {
    if (totalSpent >= 1000) return 'Style Icon';
    if (totalSpent >= 500) return 'Fashion Enthusiast';
    return 'Style Explorer';
}

function calculateStyleMatch(wishlist) {
    const baseMatch = 65;
    const wishlistBonus = Math.min((wishlist?.products?.length || 0) * 2, 20);
    return Math.min(baseMatch + wishlistBonus, 95);
}

function generateStyleSuggestions(wishlist) {
    const baseSuggestions = [
        {
            title: "Casual Summer Outfits",
            description: "Perfect for your climate and recent views",
            tags: ["Summer", "Casual", "Light Fabrics"]
        },
        {
            title: "Business Formal Attire",
            description: "Based on your saved formal wear",
            tags: ["Formal", "Office", "Professional"]
        },
        {
            title: "Weekend Comfort Styles",
            description: "Relaxed outfits for your downtime",
            tags: ["Comfort", "Casual", "Relaxed"]
        }
    ];

    return baseSuggestions;
}

function generatePriceAlerts(wishlist) {
    if (!wishlist?.products?.length) {
        return [
            {
                item: "Demo Product 1",
                priceDropped: true,
                discount: 15,
                oldPrice: 45.99,
                newPrice: 39.09
            },
            {
                item: "Demo Product 2",
                priceDropped: false,
                discount: 0,
                oldPrice: null,
                newPrice: 29.99
            }
        ];
    }

    return wishlist.products.slice(0, 3).map((product, index) => ({
        item: product.name,
        priceDropped: index === 0,
        discount: index === 0 ? 15 : 0,
        oldPrice: index === 0 ? product.price * 1.15 : null,
        newPrice: product.price,
        productId: product._id
    }));
}

function getFavoriteCategory(wishlist) {
    const categories = {};

    wishlist?.products?.forEach(product => {
        categories[product.category] = (categories[product.category] || 0) + 1;
    });

    let favorite = 'Fashion';
    let maxCount = 0;

    for (const [category, count] of Object.entries(categories)) {
        if (count > maxCount) {
            maxCount = count;
            favorite = category;
        }
    }

    return favorite;
}