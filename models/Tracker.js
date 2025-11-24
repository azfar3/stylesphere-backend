import mongoose from 'mongoose';

const trackerSchema = new mongoose.Schema({
    user: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    product: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Product',
        required: true
    },
    productName: { type: String, required: true },
    currentPrice: { type: Number, required: true },
    image: { type: String, required: true },
    isActive: { type: Boolean, default: true },

    mlInsights: {
        predictedPrice: Number,
        confidence: Number,
        trend: String,
        priceChangePercent: Number,
        recommendation: String,
        factors: [{
            factor: String,
            impact: String,
            weight: Number,
            description: String
        }],
        modelType: { type: String, default: 'fallback' },
        lastPrediction: Date,
        accuracy: Number
    },

    priceHistory: [{
        price: Number,
        date: { type: Date, default: Date.now }
    }],
    lastNotified: Date
}, {
    timestamps: true
});

trackerSchema.index({ user: 1, product: 1 }, {
    unique: true,
    partialFilterExpression: { isActive: true }
});

export default mongoose.model('Tracker', trackerSchema);