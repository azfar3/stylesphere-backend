import express from 'express';
import multer from 'multer';
import path from 'path';
import fs from 'fs';
import {
  getStyleAdvice,
  getOutfitRecommendations,
  getColorRecommendations,
  uploadImageForAnalysis
} from '../controllers/styleAdvisorController.js';
import { protect } from '../middleware/authMiddleware.js';
import { body } from 'express-validator';
import { handleValidationErrors } from '../middleware/validationMiddleware.js';

const router = express.Router();

// Ensure uploads directory exists
const uploadsDir = path.join(process.cwd(), 'uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

// Configure multer for image uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadsDir);
  },
  filename: (req, file, cb) => {
    // Generate unique filename
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

// File filter for images only
const fileFilter = (req, file, cb) => {
  if (file.mimetype.startsWith('image/')) {
    cb(null, true);
  } else {
    cb(new Error('Only image files are allowed!'), false);
  }
};

// Configure multer
const upload = multer({
  storage: storage,
  limits: {
    fileSize: 5 * 1024 * 1024, // 5MB limit
  },
  fileFilter: fileFilter,
});

// Validation middleware for style advice
const validateStyleAdvice = [
  body('gender')
    .isIn(['male', 'female'])
    .withMessage('Gender must be either male or female'),
  body('event')
    .isLength({ min: 2, max: 50 })
    .withMessage('Event type must be between 2 and 50 characters'),
  body('age')
    .optional()
    .isInt({ min: 13, max: 100 })
    .withMessage('Age must be between 13 and 100'),
  body('skin_tone')
    .optional()
    .isIn(['warm', 'cool', 'neutral'])
    .withMessage('Skin tone must be warm, cool, or neutral'),
  handleValidationErrors
];

// Validation middleware for outfit recommendations
const validateOutfitRecommendations = [
  body('occasion')
    .isLength({ min: 2, max: 50 })
    .withMessage('Occasion must be between 2 and 50 characters'),
  handleValidationErrors
];

// Validation middleware for color recommendations
const validateColorRecommendations = [
  body('skin_tone')
    .isIn(['warm', 'cool', 'neutral'])
    .withMessage('Skin tone must be warm, cool, or neutral'),
  handleValidationErrors
];

// Style advice endpoint
router.post('/advice', protect, validateStyleAdvice, getStyleAdvice);

// Outfit recommendations endpoint
router.post('/outfits', protect, validateOutfitRecommendations, getOutfitRecommendations);

// Color palette recommendations endpoint
router.post('/colors', protect, validateColorRecommendations, getColorRecommendations);

// Image analysis endpoint with multer middleware
router.post('/analyze-image', protect, upload.single('image'), uploadImageForAnalysis);

export default router;
