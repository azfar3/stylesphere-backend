import express from 'express';
import { 
  getStyleAdvice, 
  getOutfitRecommendations, 
  getColorRecommendations, 
  uploadImageForAnalysis 
} from '../controllers/styleAdvisorController.js';
import { authMiddleware } from '../middleware/authMiddleware.js';
import { validationMiddleware } from '../middleware/validationMiddleware.js';
import multer from 'multer';
import path from 'path';

const router = express.Router();

// Configure multer for image uploads
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, 'uploads/');
  },
  filename: function (req, file, cb) {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({ 
  storage: storage,
  limits: {
    fileSize: 5 * 1024 * 1024, // 5MB limit
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = /jpeg|jpg|png|gif/;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);

    if (mimetype && extname) {
      return cb(null, true);
    } else {
      cb(new Error('Only image files are allowed!'), false);
    }
  }
});

// Style advice routes
router.post('/advice', authMiddleware, validationMiddleware.validateStyleAdvice, getStyleAdvice);

// Outfit recommendations
router.post('/outfits', authMiddleware, getOutfitRecommendations);

// Color recommendations
router.post('/colors', authMiddleware, getColorRecommendations);

// Image analysis for skin tone detection
router.post('/analyze-image', authMiddleware, upload.single('image'), uploadImageForAnalysis);

export default router;
