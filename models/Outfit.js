import mongoose from 'mongoose';

const outfitSchema = new mongoose.Schema({
    user: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    stylePreferences: [String],
    suggestedItems: [String]
});

export default mongoose.model('Outfit', outfitSchema);