import mongoose from 'mongoose';

const trackerSchema = new mongoose.Schema({
    user: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    product: { type: mongoose.Schema.Types.ObjectId, ref: 'Product' },
    targetPrice: Number,
    active: { type: Boolean, default: true }
});

export default mongoose.model('Tracker', trackerSchema);