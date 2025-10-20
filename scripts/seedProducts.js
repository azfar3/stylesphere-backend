import mongoose from 'mongoose';
import dotenv from 'dotenv';
import Product from '../models/Product.js';
import connectDB from '../config/db.js';

// Load environment variables
dotenv.config();

const sampleProducts = [
    {
        name: "Classic Denim Jacket",
        brand: "StyleMax",
        price: 2500,
        originalPrice: 3000,
        image: "https://images.unsplash.com/photo-1544966503-7cc4ac882d5b?w=400",
        description: "A timeless denim jacket perfect for any casual occasion. Made from high-quality denim with classic styling.",
        category: "clothing",
        tags: ["denim", "jacket", "casual", "unisex", "classic"],
        rating: 4.5,
        reviewCount: 128,
        inStock: true,
        stockQuantity: 25,
        size: ["S", "M", "L", "XL"],
        color: ["Blue", "Light Blue", "Dark Blue"],
        material: "100% Cotton Denim",
        discount: 15,
        featured: true,
        vendor: {
            name: "StyleMax Store",
            url: "https://stylemax.com",
            contact: "info@stylemax.com"
        }
    },
    {
        name: "Elegant Silk Scarf",
        brand: "LuxeAccessories",
        price: 1200,
        originalPrice: 1500,
        image: "https://images.unsplash.com/photo-1601924994987-69e26d50dc26?w=400",
        description: "Luxurious silk scarf with beautiful patterns. Perfect accessory for any outfit.",
        category: "accessories",
        tags: ["silk", "scarf", "elegant", "luxury", "pattern"],
        rating: 4.8,
        reviewCount: 89,
        inStock: true,
        stockQuantity: 15,
        size: ["One Size"],
        color: ["Red", "Blue", "Gold", "Green"],
        material: "100% Mulberry Silk",
        discount: 20,
        featured: true,
        vendor: {
            name: "LuxeAccessories",
            url: "https://luxeaccessories.com",
            contact: "support@luxeaccessories.com"
        }
    },
    {
        name: "Comfortable Running Shoes",
        brand: "SportFit",
        price: 4200,
        originalPrice: 5000,
        image: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
        description: "High-performance running shoes with advanced cushioning technology. Perfect for daily runs and workouts.",
        category: "footwear",
        tags: ["running", "shoes", "sport", "comfortable", "athletic"],
        rating: 4.6,
        reviewCount: 256,
        inStock: true,
        stockQuantity: 40,
        size: ["6", "7", "8", "9", "10", "11"],
        color: ["Black", "White", "Grey", "Blue"],
        material: "Synthetic Mesh Upper",
        discount: 16,
        featured: true,
        vendor: {
            name: "SportFit",
            url: "https://sportfit.com",
            contact: "orders@sportfit.com"
        }
    },
    {
        name: "Designer Handbag",
        brand: "ChicBags",
        price: 8500,
        originalPrice: 10000,
        image: "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400",
        description: "Premium leather handbag with elegant design. Perfect for professional and casual settings.",
        category: "bags",
        tags: ["handbag", "leather", "designer", "elegant", "professional"],
        rating: 4.7,
        reviewCount: 94,
        inStock: true,
        stockQuantity: 12,
        size: ["One Size"],
        color: ["Black", "Brown", "Tan", "Navy"],
        material: "Genuine Leather",
        discount: 15,
        featured: false,
        vendor: {
            name: "ChicBags",
            url: "https://chicbags.com",
            contact: "info@chicbags.com"
        }
    },
    {
        name: "Gold Chain Necklace",
        brand: "JewelCraft",
        price: 12000,
        originalPrice: 15000,
        image: "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=400",
        description: "18K gold plated chain necklace with exquisite craftsmanship. A perfect accessory for special occasions.",
        category: "jewelry",
        tags: ["necklace", "gold", "chain", "jewelry", "elegant"],
        rating: 4.9,
        reviewCount: 67,
        inStock: true,
        stockQuantity: 8,
        size: ["16 inch", "18 inch", "20 inch"],
        color: ["Gold"],
        material: "18K Gold Plated",
        discount: 20,
        featured: true,
        vendor: {
            name: "JewelCraft",
            url: "https://jewelcraft.com",
            contact: "support@jewelcraft.com"
        }
    },
    {
        name: "Moisturizing Face Cream",
        brand: "GlowSkin",
        price: 1800,
        originalPrice: 2200,
        image: "https://images.unsplash.com/photo-1556228724-2ed52b44d33b?w=400",
        description: "Advanced moisturizing face cream with natural ingredients. Suitable for all skin types.",
        category: "beauty",
        tags: ["skincare", "moisturizer", "face cream", "natural", "beauty"],
        rating: 4.4,
        reviewCount: 145,
        inStock: true,
        stockQuantity: 30,
        size: ["50ml", "100ml"],
        color: ["White"],
        material: "Natural Ingredients",
        discount: 18,
        featured: false,
        vendor: {
            name: "GlowSkin Beauty",
            url: "https://glowskin.com",
            contact: "care@glowskin.com"
        }
    },
    {
        name: "Cotton Casual T-Shirt",
        brand: "ComfortWear",
        price: 850,
        originalPrice: 1100,
        image: "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400",
        description: "Soft and comfortable cotton t-shirt perfect for everyday wear. Available in multiple colors.",
        category: "clothing",
        tags: ["t-shirt", "cotton", "casual", "comfortable", "everyday"],
        rating: 4.3,
        reviewCount: 312,
        inStock: true,
        stockQuantity: 60,
        size: ["XS", "S", "M", "L", "XL", "XXL"],
        color: ["White", "Black", "Grey", "Navy", "Red"],
        material: "100% Cotton",
        discount: 23,
        featured: false,
        vendor: {
            name: "ComfortWear",
            url: "https://comfortwear.com",
            contact: "orders@comfortwear.com"
        }
    },
    {
        name: "Wireless Bluetooth Headphones",
        brand: "TechSound",
        price: 3500,
        originalPrice: 4500,
        image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
        description: "High-quality wireless Bluetooth headphones with noise cancellation and long battery life.",
        category: "electronics",
        tags: ["headphones", "wireless", "bluetooth", "audio", "technology"],
        rating: 4.5,
        reviewCount: 198,
        inStock: true,
        stockQuantity: 20,
        size: ["One Size"],
        color: ["Black", "White", "Silver"],
        material: "Premium Plastic and Metal",
        discount: 22,
        featured: true,
        vendor: {
            name: "TechSound",
            url: "https://techsound.com",
            contact: "support@techsound.com"
        }
    }
];

const seedProducts = async () => {
    try {
        // Connect to database
        await connectDB();
        
        console.log('🔄 Connected to MongoDB. Starting product seeding...');
        
        // Clear existing products (optional - comment out if you want to keep existing data)
        // await Product.deleteMany({});
        // console.log('✅ Cleared existing products');
        
        // Insert sample products
        const createdProducts = await Product.insertMany(sampleProducts);
        
        console.log(`✅ Successfully seeded ${createdProducts.length} products:`);
        createdProducts.forEach(product => {
            console.log(`   - ${product.name} (${product.brand}) - ₹${product.price}`);
        });
        
        console.log('\n🎉 Product seeding completed successfully!');
        process.exit(0);
        
    } catch (error) {
        console.error('❌ Error seeding products:', error.message);
        if (error.name === 'ValidationError') {
            Object.keys(error.errors).forEach(key => {
                console.error(`   Validation Error in ${key}: ${error.errors[key].message}`);
            });
        }
        process.exit(1);
    }
};

// Run the seeding function
seedProducts();
