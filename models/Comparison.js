import mongoose from 'mongoose';

const comparisonSchema = new mongoose.Schema({
    userId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    productIds: [{
        type: String,
        required: true
    }],
    comparisonData: [{
        id: String,
        name: String,
        brand: String,
        category: String,
        price: Number,
        originalPrice: Number,
        discount: Number,
        image: String,
        rating: Number,
        description: String,
        productType: String,
        fitType: String,
        materialType: String,
        primaryColor: String,
        sizeVariant: String,
        styleType: String,
        inStock: Boolean,
        stockQuantity: Number
    }],
    name: {
        type: String,
        default: ''
    },
    comparedAt: {
        type: Date,
        default: Date.now
    },
    savedAt: {
        type: Date
    },
    isSaved: {
        type: Boolean,
        default: false
    }
}, {
    timestamps: true
});

comparisonSchema.index({ userId: 1, comparedAt: -1 });
comparisonSchema.index({ userId: 1, isSaved: 1 });

export default mongoose.model('Comparison', comparisonSchema);