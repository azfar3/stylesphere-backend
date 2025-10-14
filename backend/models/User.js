import mongoose from 'mongoose';

const userSchema = new mongoose.Schema({
    name: {
        type: String,
        required: [true, 'Name is required'],
        trim: true,
        minlength: [2, 'Name must be at least 2 characters'],
        maxlength: [50, 'Name cannot exceed 50 characters']
    },
    email: {
        type: String,
        unique: true,
        required: [true, 'Email is required'],
        lowercase: true,
        trim: true,
        match: [/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/, 'Please enter a valid email']
    },
    password: {
        type: String,
        required: [true, 'Password is required'],
        select: false,
        minlength: [6, 'Password must be at least 6 characters']
    },
    role: {
        type: String,
        enum: ['user', 'admin'],
        default: 'user'
    },
    wishlist: [{
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Product'
    }],
    trackingEnabled: [{
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Product'
    }],
    lastLoginAt: {
        type: Date,
        default: null
    },
    preferences: {
        type: Object,
        default: {}
    }
}, {
    timestamps: true
});

userSchema.index({ email: 1 });
userSchema.index({ createdAt: -1 });

export default mongoose.model('User', userSchema);