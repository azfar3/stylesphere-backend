import mongoose from 'mongoose';

const pricePredictionSchema = new mongoose.Schema({
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
  currentPrice: {
    type: Number,
    required: true,
    min: 0
  },
  predictedPrice: {
    type: Number,
    required: true,
    min: 0
  },
  predictionDate: {
    type: Date,
    default: Date.now
  },
  targetDate: {
    type: Date,
    required: true
  },
  confidence: {
    type: Number,
    min: 0,
    max: 100,
    default: 80
  },
  trend: {
    type: String,
    enum: ['increasing', 'decreasing', 'stable'],
    default: 'stable'
  },
  factors: [{
    factor: {
      type: String,
      required: true
    },
    impact: {
      type: String,
      enum: ['positive', 'negative', 'neutral'],
      default: 'neutral'
    },
    weight: {
      type: Number,
      min: 0,
      max: 1,
      default: 0.5
    }
  }],
  historicalData: [{
    date: {
      type: Date,
      required: true
    },
    price: {
      type: Number,
      required: true,
      min: 0
    }
  }],
  accuracy: {
    type: Number,
    min: 0,
    max: 100
  },
  status: {
    type: String,
    enum: ['pending', 'active', 'completed', 'expired'],
    default: 'active'
  },
  notifications: {
    emailSent: {
      type: Boolean,
      default: false
    },
    smsSet: {
      type: Boolean,
      default: false
    }
  }
}, {
  timestamps: true
});

// Index for efficient queries
pricePredictionSchema.index({ user: 1, product: 1 });
pricePredictionSchema.index({ targetDate: 1, status: 1 });
pricePredictionSchema.index({ createdAt: -1 });

// Methods
pricePredictionSchema.methods.updateAccuracy = function(actualPrice) {
  const priceDifference = Math.abs(this.predictedPrice - actualPrice);
  const percentageError = (priceDifference / actualPrice) * 100;
  this.accuracy = Math.max(0, 100 - percentageError);
  return this.save();
};

pricePredictionSchema.methods.isExpired = function() {
  return new Date() > this.targetDate;
};

// Static methods
pricePredictionSchema.statics.getUserPredictions = function(userId, limit = 10) {
  return this.find({ user: userId })
    .populate('product', 'name image price category')
    .sort({ createdAt: -1 })
    .limit(limit);
};

pricePredictionSchema.statics.getActivePredictions = function(userId) {
  return this.find({ 
    user: userId, 
    status: 'active',
    targetDate: { $gte: new Date() }
  })
  .populate('product', 'name image price category')
  .sort({ targetDate: 1 });
};

const PricePrediction = mongoose.model('PricePrediction', pricePredictionSchema);

export default PricePrediction;
