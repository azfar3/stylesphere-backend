const mongoose = require('mongoose');

const priceHistorySchema = new mongoose.Schema({
    productId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Product',
        required: true
    },
    price: {
        type: Number,
        required: true
    },
    date: {
        type: Date,
        default: Date.now
    },
    source: {
        type: String,
        default: 'website'
    }
}, {
    timestamps: true
});

priceHistorySchema.index({ productId: 1, date: -1 });

module.exports = mongoose.model('PriceHistory', priceHistorySchema);