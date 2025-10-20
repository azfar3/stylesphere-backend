import mongoose from 'mongoose';

const productSchema = new mongoose.Schema({
    product_id: {
        type: String,
        required: true,
        unique: true
    },
    title: {
        type: String,
        required: true,
        trim: true
    },
    brand: {
        type: String,
        required: true,
        trim: true
    },
    category: {
        type: String,
        required: true,
        trim: true
    },
    product_url: {
        type: String,
        trim: true
    },
    image_url: {
        type: String,
        trim: true
    },
    price_clean: {
        type: Number,
        required: true,
        min: 0
    },
    original_price_clean: {
        type: Number,
        min: 0
    },
    sale_price_clean: {
        type: Number,
        min: 0
    },
    discount_clean: {
        type: Number,
        min: 0,
        max: 100,
        default: 0
    },
    is_discounted: {
        type: Boolean,
        default: false
    },
    price_tier: {
        type: String,
        trim: true
    },
    savings: {
        type: Number,
        min: 0,
        default: 0
    },
    savings_percentage: {
        type: Number,
        min: 0,
        max: 100,
        default: 0
    },
    discount_level: {
        type: String,
        trim: true
    },
    product_type: {
        type: String,
        trim: true
    },
    primary_color: {
        type: String,
        trim: true
    },
    material_type: {
        type: String,
        trim: true
    },
    fit_type: {
        type: String,
        trim: true
    },
    size_variant: {
        type: String,
        trim: true
    },
    style_type: {
        type: String,
        trim: true
    },
    title_length: {
        type: Number,
        min: 0
    },
    has_image: {
        type: Boolean,
        default: false
    },
    availability: {
        type: Boolean,
        default: true
    },
    local_image_path: {
        type: String,
        trim: true
    }
}, {
    timestamps: true,
    collection: 'new_products',
    toJSON: { virtuals: true },
    toObject: { virtuals: true }
});

productSchema.virtual('name').get(function () {
    return this.title || 'Unnamed Product';
});

productSchema.virtual('price').get(function () {
    return this.sale_price_clean || this.price_clean;
});

productSchema.virtual('originalPrice').get(function () {
    return this.original_price_clean || this.price_clean;
});

productSchema.virtual('discount').get(function () {
    let discount = this.discount_clean || 0;
    const effectivePrice = this.sale_price_clean || this.price_clean;
    const originalPrice = this.original_price_clean || this.price_clean;

    if (!discount && originalPrice > effectivePrice) {
        discount = Math.round(((originalPrice - effectivePrice) / originalPrice) * 100);
    }
    return Math.min(discount, 100);
});

productSchema.virtual('image').get(function () {
    // `http://localhost:5000/images/${this.local_image_path.replace(/\\/g, '/')}`
    return this.image_url;
});

productSchema.virtual('tags').get(function () {
    const tags = new Set();
    if (this.brand) tags.add(this.brand.toLowerCase());
    if (this.category) tags.add(this.category.toLowerCase());
    if (this.product_type) tags.add(this.product_type.toLowerCase());
    if (this.fit_type) tags.add(this.fit_type.toLowerCase());
    if (this.style_type) tags.add(this.style_type.toLowerCase());
    if (this.primary_color) tags.add(this.primary_color.toLowerCase());
    if (this.price_tier) tags.add(this.price_tier.toLowerCase());

    if (tags.size === 0) {
        tags.add('fashion');
        tags.add('clothing');
    }

    return Array.from(tags);
});

productSchema.virtual('rating').get(function () {
    return 4.0;
});

productSchema.virtual('reviewCount').get(function () {
    return Math.floor(Math.random() * 100) + 10;
});

productSchema.virtual('inStock').get(function () {
    return this.availability !== false;
});

productSchema.virtual('stockQuantity').get(function () {
    return this.availability ? Math.floor(Math.random() * 50) + 10 : 0;
});

productSchema.virtual('size').get(function () {
    if (!this.size_variant) return ['S', 'M', 'L', 'XL'];
    const sizeMap = {
        'small': 'S', 'medium': 'M', 'large': 'L', 'xlarge': 'XL', 'xl': 'XL', 'xxl': 'XXL'
    };
    const normalized = this.size_variant.toLowerCase().trim();
    return [sizeMap[normalized] || this.size_variant.toUpperCase()];
});

productSchema.virtual('color').get(function () {
    return this.primary_color ? [this.primary_color] : ['Black'];
});

productSchema.virtual('material').get(function () {
    return this.material_type;
});

productSchema.virtual('featured').get(function () {
    return false;
});

productSchema.virtual('isActive').get(function () {
    return true;
});

productSchema.virtual('images').get(function () {
    return this.image_url ? [this.image_url] : [];
});

productSchema.virtual('metadata').get(function () {
    return {
        product_url: this.product_url,
        price_tier: this.price_tier,
        savings: this.savings,
        product_type: this.product_type,
        fit_type: this.fit_type,
        style_type: this.style_type,
        discount_level: this.discount_level,
        is_discounted: this.is_discounted
    };
});

productSchema.virtual('description').get(function () {
    const descriptionParts = [];
    if (this.brand) descriptionParts.push(this.brand);
    if (this.title) descriptionParts.push(this.title);
    if (this.style_type) descriptionParts.push(`Style: ${this.style_type}`);
    if (this.fit_type) descriptionParts.push(`Fit: ${this.fit_type}`);
    if (this.material_type) descriptionParts.push(`Material: ${this.material_type}`);

    return descriptionParts.join(' - ') || 'Product description not available';
});

productSchema.index({ brand: 1 });
productSchema.index({ category: 1 });
productSchema.index({ price_clean: 1 });
productSchema.index({ title: 'text', brand: 'text' });
productSchema.index({ product_type: 1 });
productSchema.index({ availability: 1 });

export default mongoose.model('Product', productSchema);