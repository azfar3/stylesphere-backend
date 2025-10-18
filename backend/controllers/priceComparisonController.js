import Product from '../models/Product.js';
import mongoose from 'mongoose';

export const getProductTypes = async (req, res) => {
  try {
    const productTypes = await Product.distinct('product_type', {
      product_type: { $exists: true, $ne: "" }
    });
    res.json({
      success: true,
      data: productTypes.filter(Boolean).sort()
    });
  } catch (error) {
    console.error('Get product types error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch product types'
    });
  }
};

export const getComparisonData = async (req, res) => {
  try {
    const { productType, fitType, search, minPrice, maxPrice, limit = 50 } = req.query;

    let query = {};

    if (productType) {
      query.product_type = { $regex: productType, $options: 'i' };
    }

    if (fitType && fitType !== 'all') {
      query.fit_type = { $regex: fitType, $options: 'i' };
    }

    if (search) {
      const searchRegex = { $regex: search, $options: 'i' };
      query.$or = [
        { title: searchRegex },
        { brand: searchRegex },
        { primary_color: searchRegex },
        { material_type: searchRegex }
      ];
    }

    if (minPrice || maxPrice) {
      query.price_clean = {};
      if (minPrice) query.price_clean.$gte = parseInt(minPrice) || 0;
      if (maxPrice) query.price_clean.$lte = parseInt(maxPrice) || 999999;
    }

    const products = await Product.find(query)
      .sort({ price_clean: 1 })
      .limit(parseInt(limit))
      .select(`
        product_id title brand product_type fit_type material_type primary_color
        price_clean original_price_clean sale_price_clean discount_clean is_discounted
        price_tier savings savings_percentage discount_level
        image_url images image category tags availability
        local_image_path product_url
      `)
      .lean();

    const availableBrands = [...new Set(products.map(p => p.brand).filter(Boolean))];
    const availableProductTypes = [...new Set(products.map(p => p.product_type).filter(Boolean))];
    const comparisonGroups = createEnhancedComparisonGroups(products);
    const stats = calculateEnhancedStats(products, comparisonGroups);

    res.json({
      success: true,
      data: {
        products: comparisonGroups,
        stats,
        availableBrands,
        availableProductTypes
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
    res.json({ success: true, data: priceHistory });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to fetch price trends'
    });
  }
};

function createEnhancedComparisonGroups(products) {
  const comparisonMap = new Map();

  products.forEach(product => {
    const groupKey = createEnhancedGroupKey(product);

    if (!comparisonMap.has(groupKey)) {
      comparisonMap.set(groupKey, {
        id: product.product_id,
        product_id: product.product_id,
        title: product.title,
        name: product.title,
        image_url: product.image_url,
        image: product.image_url,
        category: product.category,
        product_type: product.product_type,
        fit_type: product.fit_type,
        material_type: product.material_type,
        primary_color: product.primary_color,
        prices: {},
        brands: [],
        productCount: 0,
        minPrice: Infinity,
        maxPrice: 0,
        availability: product.availability,
        product_url: product.product_url
      });
    }

    const group = comparisonMap.get(groupKey);

    if (product.brand && product.price_clean) {
      group.prices[product.brand] = {
        price: product.price_clean,
        price_clean: product.price_clean,
        original_price_clean: product.original_price_clean,
        sale_price_clean: product.sale_price_clean,
        is_discounted: product.is_discounted,
        discount_clean: product.discount_clean,
        discount_level: product.discount_level,
        savings: product.savings,
        savings_percentage: product.savings_percentage,
        price_tier: product.price_tier,
        product_id: product.product_id,
        inStock: product.availability !== 'Out of Stock',
        hasDiscount: product.is_discounted,
        originalPrice: product.original_price_clean
      };

      if (!group.brands.includes(product.brand)) {
        group.brands.push(product.brand);
      }

      group.productCount++;
      const currentPrice = product.price_clean;
      group.minPrice = Math.min(group.minPrice, currentPrice);
      group.maxPrice = Math.max(group.maxPrice, currentPrice);
    }
  });

  return Array.from(comparisonMap.values())
    .filter(group => Object.keys(group.prices).length >= 1)
    .sort((a, b) => a.minPrice - b.minPrice);
}

function createEnhancedGroupKey(product) {
  const baseKey = product.title + '_' + product.brand;
  const attributes = [
    product.fit_type,
    product.material_type,
    product.primary_color,
    product.product_id
  ].filter(Boolean).join('_');
  return `${baseKey}_${attributes}`.toLowerCase().replace(/\s+/g, '_');
}

function calculateEnhancedStats(products, comparisonGroups) {
  if (products.length === 0) return null;

  const prices = products
    .filter(p => p.price_clean && p.price_clean > 0)
    .map(p => p.price_clean);

  if (prices.length === 0) return null;

  const total = prices.reduce((sum, price) => sum + price, 0);
  const averagePrice = Math.round(total / prices.length);
  const lowestPrice = Math.min(...prices);
  const highestPrice = Math.max(...prices);

  const discountedProducts = products.filter(p => p.is_discounted);
  const totalSavings = discountedProducts.reduce((sum, product) => sum + (product.savings || 0), 0);

  const savingsOpportunities = comparisonGroups.filter(group => {
    const groupPrices = Object.values(group.prices).map(p => p.price_clean);
    return groupPrices.length >= 2 && (Math.max(...groupPrices) - Math.min(...groupPrices)) > 100;
  });

  return {
    totalProducts: products.length,
    comparisonGroups: comparisonGroups.length,
    averagePrice,
    lowestPrice,
    highestPrice,
    discountedProducts: discountedProducts.length,
    totalSavings,
    savingsOpportunities: savingsOpportunities.length,
    bestSavings: savingsOpportunities.length > 0 ? Math.max(...savingsOpportunities.map(group => {
      const prices = Object.values(group.prices).map(p => p.price_clean);
      return Math.max(...prices) - Math.min(...prices);
    })) : 0
  };
}