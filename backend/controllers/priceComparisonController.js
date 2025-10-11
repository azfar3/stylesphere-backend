import Product from '../models/Product.js';

export const getComparisonData = async (req, res) => {
  try {

    const { category, search, minPrice, maxPrice, limit = 50 } = req.query;

    let query = { isActive: true };

    if (category && category !== 'all') {
      query.$or = [
        { category: category },
        { category: { $regex: category, $options: 'i' } },
        { tags: { $in: [new RegExp(category, 'i')] } }
      ];
    }

    if (search) {
      query.$or = [
        { name: { $regex: search, $options: 'i' } },
        { brand: { $regex: search, $options: 'i' } },
        { description: { $regex: search, $options: 'i' } }
      ];
    }

    if (minPrice || maxPrice) {
      query.price = {};
      if (minPrice) query.price.$gte = parseInt(minPrice) || 0;
      if (maxPrice) query.price.$lte = parseInt(maxPrice) || 999999;
    }

    const products = await Product.find(query)
      .sort({ name: 1 })
      .limit(parseInt(limit))
      .select('name brand price images image category tags rating discount originalPrice inStock')
      .lean();

    if (!products.length) {
      return res.json({
        success: true,
        data: {
          products: [],
          stats: null,
          availableBrands: []
        }
      });
    }

    const availableBrands = [...new Set(products.map(p => p.brand).filter(Boolean))];

    const comparisonGroups = createComparisonGroups(products);

    const stats = calculateStats(products, comparisonGroups);

    res.json({
      success: true,
      data: {
        products: comparisonGroups,
        stats,
        availableBrands
      }
    });

  } catch (error) {
    console.error('Price comparison error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch comparison data',
      error: process.env.NODE_ENV === 'development' ? error.message : 'Internal server error'
    });
  }
};

export const getPriceTrends = async (req, res) => {
  try {
    const { productId } = req.params;

    const priceHistory = [
      { date: new Date('2024-01-01'), price: 2500 },
      { date: new Date('2024-02-01'), price: 2300 },
      { date: new Date('2024-03-01'), price: 2200 },
    ];

    res.json({
      success: true,
      data: priceHistory
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to fetch price trends'
    });
  }
};

function createComparisonGroups(products) {
  const comparisonMap = new Map();

  products.forEach(product => {
    const groupKey = createGroupKey(product);

    if (!comparisonMap.has(groupKey)) {
      comparisonMap.set(groupKey, {
        id: product._id.toString(),
        name: product.name,
        image: getProductImage(product),
        category: product.category,
        prices: {},
        brands: [],
        productCount: 0,
        minPrice: Infinity,
        maxPrice: 0
      });
    }

    const group = comparisonMap.get(groupKey);

    if (product.brand && product.price) {
      group.prices[product.brand] = {
        price: product.price,
        productId: product._id.toString(),
        inStock: product.inStock !== false,
        hasDiscount: product.discount > 0,
        originalPrice: product.originalPrice || product.price
      };

      if (!group.brands.includes(product.brand)) {
        group.brands.push(product.brand);
      }

      group.productCount++;

      group.minPrice = Math.min(group.minPrice, product.price);
      group.maxPrice = Math.max(group.maxPrice, product.price);
    }
  });

  return Array.from(comparisonMap.values())
    .filter(group => Object.keys(group.prices).length >= 1)
    .sort((a, b) => b.productCount - a.productCount);
}

function createGroupKey(product) {
  const cleanName = product.name
    .toLowerCase()
    .replace(/\b(xs|s|m|l|xl|xxl|xxxl|\d+)\b/gi, '')
    .replace(/\s+/g, ' ')
    .trim();

  return `${product.category}_${cleanName}`;
}

function getProductImage(product) {
  return product.images?.[0] || product.image || '/images/placeholder.jpg';
}

function calculateStats(products, comparisonGroups) {
  if (products.length === 0) return null;

  const prices = products
    .filter(p => p.price && p.price > 0)
    .map(p => p.price);

  if (prices.length === 0) return null;

  const total = prices.reduce((sum, price) => sum + price, 0);
  const averagePrice = Math.round(total / prices.length);
  const lowestPrice = Math.min(...prices);
  const highestPrice = Math.max(...prices);

  const savingsOpportunities = comparisonGroups.filter(group => {
    const groupPrices = Object.values(group.prices).map(p => p.price);
    return groupPrices.length >= 2 && (Math.max(...groupPrices) - Math.min(...groupPrices)) > 100;
  });

  return {
    totalProducts: products.length,
    comparisonGroups: comparisonGroups.length,
    averagePrice,
    lowestPrice,
    highestPrice,
    savingsOpportunities: savingsOpportunities.length,
    bestSavings: savingsOpportunities.length > 0
      ? Math.max(...savingsOpportunities.map(group => {
        const prices = Object.values(group.prices).map(p => p.price);
        return Math.max(...prices) - Math.min(...prices);
      }))
      : 0
  };
}