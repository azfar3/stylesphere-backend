import mongoose from 'mongoose';

const userSchema = new mongoose.Schema({
    name: { type: String, required: true, trim: true },
    email: { type: String, unique: true, required: true, lowercase: true, trim: true },
    password: { type: String, required: true, select: false },
    role: { type: String, enum: ['user', 'admin'], default: 'user' },
    wishlist: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Product' }],
    trackingEnabled: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Product' }],
    lastLoginAt: { type: Date },
    preferences: { type: Object, default: {} }
}, {
    timestamps: true
});

export default mongoose.model('User', userSchema);