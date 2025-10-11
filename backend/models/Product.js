import mongoose from 'mongoose';

const productSchema = new mongoose.Schema({
    name: {
        type: String,
        required: [true, 'Product name is required'],
        trim: true,
        maxLength: [200, 'Product name cannot exceed 200 characters']
    },
    brand: {
        type: String,
        required: [true, 'Brand is required'],
        trim: true,
        maxLength: [100, 'Brand name cannot exceed 100 characters']
    },
    price: {
        type: Number,
        required: [true, 'Price is required'],
        min: [0, 'Price cannot be negative']
    },
    originalPrice: {
        type: Number,
        min: [0, 'Original price cannot be negative']
    },
    image: {
        type: String,
        required: [true, 'Product image is required'],
        trim: true
    },
    images: [{
        type: String,
        trim: true
    }],
    description: {
        type: String,
        trim: true,
        maxLength: [1000, 'Description cannot exceed 1000 characters']
    },
    category: {
        type: String,
        required: [true, 'Category is required'],
        trim: true,
        enum: {
            values: [
                "men", "men1", "men1-a", "men1-b", "men2", "men3", "men4", "men5", "men6", "men7", "men8", "men9", "men10", "men11", "men12", "men13", "men14",
                "men-new-arrival", "men-new-arrival2", "men-new-arrival3", "men-new-arrival4", "men-new-arrival5", "men-new-arrival6", "men-new-arrival7", "men-new-arrival8",
                "men-new-arrival9", "men-new-arrival10", "men-new-arrival11", "men-new-arrival12", "men-new-arrival13", "men-new-arrival14", "men-new-arrival15", "men-t-shirts",
                "men-shirts", "men-polo-shirts", "men-activewear", "men-trousers", "men-shorts", "men-jeans", "men-t-shirts-sale", "men-polo-sale", "men-trousers-sale", "men-jeans-sale",
                "men-activewear-sale", "men-shirt-sale", "men-shorts-sale", "men-polo", "men-tank-tops", "men-pants", "men-jacket", "men-sweaters", "men-hoodies", "men-sweatshirts",
                "men-sale", "men-shirts-sale", "men-tank-tops-sale", "men-pants-sale", "men-jacket-sale", "men-sweaters-sale", "men-hoodies-sale", "men-sweatshirts-sale", "mens-unstitched",
                "mens-pret", "men-p2", "men-p3", "men-p4", "men-p5", "men-p6", "men-p7", "men-p8", "men-p9", "men-p10", "men-p11", "men-p12", "men-p13", "men-p14", "men-p15", "men15", "men16",
                "men17", "men18", "men19", "men20", "men21", "men22", "men23", "men24", "men25", "men26", "men27", "men28",

                "women1", "women2", "women2-a", "women2-b", "women3", "women4", "women4-a", "women5", "women5-a", "women6", "women6-a", "women7", "women7-a", "women8", "women9", "women10",
                "women10-a", "women11", "women12", "women13", "women14", "women15", "women16", "women17", "women18", "women-new-arrival", "women-shirts", "women-t-shirts", "women-polos",
                "women-dresses-and-jumpsuits", "women-shirts-and-shorts", "women-jeans", "women-trousers",
                "women-activewear", "women", "women-t-shirts-sale", "women-shirts-sale", "women-polo-sale", "women-shorts-sale", "women-jumpsuits-sale", "women-activewear-sale",
                "women-trousers-sale", "women-jeans-sale", "women-tops", "women-dresses", "women-jumpsuits", "women-camisoles", "women-jacket", "women-sweaters", "women-hoodies",
                "women-sweatshirts", "women-co-ords", "women-coats", "women-sale", "women-tops-sale", "women-dresses-sale", "women-camisoles-sale", "women-jacket-sale", "women-sweaters-sale",
                "women-hoodies-sale", "women-sweatshirts-sale", "women-co-ords-sale", "women-coats-sale", "womens-unstitched", "womens-pret", "women-p2", "women-p3", "women-p4",
                "women-p5", "women19", "women20", "women21", "women22", "women23", "women24", "women25", "women26", "women27", "women28",

                "baby-girls-shirts", "baby-girls-t-shirts", "baby-girls-dresses", "baby-girls-suit", "baby-girls-skirts-and-shorts", "baby-girls-trousers", "baby-girls-jeans",
                "girls-shirts", "girls-t-shirts", "girls-dresses-and-jumpsuit", "girls-suit", "girls-skirts", "girls-trousers", "girls-jeans", "girl-t-shirts-sale", "girl-shirts-sale",
                "girl-co-ord-sets-sale", "girl-dress-sale", "girls-skirt-and-short-sale", "girl-trousers-sale", "girl-jeans-sale", "girls-winter-sale", "girls", "girls-tops", "girls-bottoms",
                "girls-jumpsuits", "girls-camisoles", "girls-jacket", "girls-sweaters", "girls-hoodies", "girls-sweatshirts", "girls-co-ords", "girls-sale", "girls-tops-sale",
                "girls-bottoms-sale", "girls-camisoles-sale", "girls-jacket-sale", "girls-sweaters-sale", "girls-hoodies-sale", "girls-sweatshirts-sale",
                "girls-co-ords-sale", "girls1", "girls2", "girls3", "girls4", "girls5", "girls6", "girls7", "girls8", "girls9", "girls10", "girls11", "girls12", "girls13",

                "baby-boy-shirt", "baby-boy-t-shirt", "baby-boys-suits", "baby-boy-dungaree-1", "baby-boys-shorts", "baby-boy-trousers-1", "baby-boy-jeans", "juniors-boy-shirts",
                "juniors-boy-t-shirts", "juniors-boy-co-ord-sets", "junior-boy-shorts", "junior-boys-trousers", "juniors-boy-jeans", "boy-t-shirts-sale", "boy-shirts-sale",
                "boy-co-ord-sets-sale", "boys-dungaree-sale", "boy-shorts-sale", "boy-trousers-sale", "boy-jeans-sale", "boys", "boys-polo", "boys-t-shirts", "boys-shirts", "boys-trousers",
                "boys-jeans", "boys-pants", "boys-shorts", "boys-jacket", "boys-sweaters", "boys-hoodies", "boys-sweatshirts", "boys-sale", "boys-polo-sale", "boys-shirts-sale",
                "boys-pants-sale", "boys-jacket-sale", "boys-sweaters-sale", "boys-hoodies-sale", "boys-sweatshirts-sale",
                "boys1", "boys2", "boys3", "boys4", "boys5", "boys6", "boys7", "boys8", "boys9", "boys10", "boys11", "boys12", "boys13", "boys14",

                "kids-sale", "ideas-home", "sale",
            ],
            message: '{VALUE} is not a valid category'
        }
    },
    tags: [{
        type: String,
        trim: true,
        lowercase: true
    }],
    rating: {
        type: Number,
        min: [0, 'Rating cannot be less than 0'],
        max: [5, 'Rating cannot be more than 5'],
        default: 0
    },
    reviewCount: {
        type: Number,
        min: [0, 'Review count cannot be negative'],
        default: 0
    },
    inStock: {
        type: Boolean,
        default: true
    },
    stockQuantity: {
        type: Number,
        min: [0, 'Stock quantity cannot be negative'],
        default: 0
    },
    sku: {
        type: String,
        trim: true,
        unique: true,
        sparse: true
    },
    size: [{
        type: String,
        trim: true,
        enum: [
            'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL', 'Free Size', 'One Size',
            '5', '5.5', '6', '6.5', '7', '7.5', '8', '8.5', '9', '9.5',
            '10', '10.5', '11', '11.5', '12', '12.5', '13',
            '14 inch', '16 inch', '18 inch', '20 inch', '22 inch', '24 inch',
            '30ml', '50ml', '100ml', '150ml', '200ml', '250ml', '500ml'
        ]
    }],
    color: [{
        type: String,
        trim: true
    }],
    material: {
        type: String,
        trim: true
    },
    discount: {
        type: Number,
        min: [0, 'Discount cannot be negative'],
        max: [100, 'Discount cannot exceed 100%'],
        default: 0
    },
    featured: {
        type: Boolean,
        default: false
    },
    isActive: {
        type: Boolean,
        default: true
    },
    createdBy: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User'
    },
    vendor: {
        name: {
            type: String,
            trim: true
        },
        url: {
            type: String,
            trim: true
        },
        contact: {
            type: String,
            trim: true
        }
    },
    vendorPrices: [{
        vendor: {
            type: String,
            required: true,
            trim: true
        },
        price: {
            type: Number,
            required: true,
            min: 0
        },
        url: {
            type: String,
            trim: true
        },
        inStock: {
            type: Boolean,
            default: true
        },
        lastUpdated: {
            type: Date,
            default: Date.now
        }
    }],
    comparisonKey: {
        type: String,
        trim: true,
        lowercase: true
    }
}, {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true }
});

productSchema.virtual('discountedPrice').get(function () {
    if (this.discount && this.discount > 0) {
        return Math.round(this.price * (1 - this.discount / 100));
    }
    return this.price;
});

productSchema.virtual('savings').get(function () {
    if (this.discount && this.discount > 0) {
        return Math.round(this.price * (this.discount / 100));
    }
    return 0;
});

productSchema.index({ name: 'text', brand: 'text', description: 'text' });
productSchema.index({ category: 1 });
productSchema.index({ brand: 1 });
productSchema.index({ price: 1 });
productSchema.index({ rating: -1 });
productSchema.index({ featured: -1, createdAt: -1 });
productSchema.index({ tags: 1 });
productSchema.index({ isActive: 1, inStock: 1 });
productSchema.index({ comparisonKey: 1, brand: 1 });

productSchema.pre('save', function (next) {
    if (!this.sku) {
        this.sku = `${this.brand?.toUpperCase().replace(/\s+/g, '')}-${this.name.toUpperCase().replace(/\s+/g, '').substring(0, 10)}-${Date.now()}`;
    }
    if (this.stockQuantity <= 0) {
        this.inStock = false;
    }
    next();
});

export default mongoose.model('Product', productSchema);
