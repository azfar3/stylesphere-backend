import { body, validationResult } from 'express-validator';

// Helper function to handle validation results
export const handleValidationErrors = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      success: false,
      error: 'Validation failed',
      details: errors.array().map(error => ({
        field: error.param,
        message: error.msg,
        value: error.value
      }))
    });
  }
  next();
};

// Auth validation rules
export const validateRegister = [
  body('email')
    .isEmail()
    .normalizeEmail()
    .withMessage('Please provide a valid email'),
  body('password')
    .isLength({ min: 6 })
    .withMessage('Password must be at least 6 characters long'),
  body('name')
    .trim()
    .isLength({ min: 2, max: 50 })
    .withMessage('Name must be between 2 and 50 characters')
    .matches(/^[a-zA-Z\s]+$/)
    .withMessage('Name can only contain letters and spaces'),
  handleValidationErrors
];

export const validateLogin = [
  body('email')
    .isEmail()
    .normalizeEmail()
    .withMessage('Please provide a valid email'),
  body('password')
    .notEmpty()
    .withMessage('Password is required'),
  handleValidationErrors
];

// Product validation rules
export const validateProduct = [
  body('name')
    .trim()
    .isLength({ min: 2, max: 100 })
    .withMessage('Product name must be between 2 and 100 characters'),
  body('price')
    .isFloat({ min: 0 })
    .withMessage('Price must be a positive number'),
  body('category')
    .trim()
    .isLength({ min: 2, max: 50 })
    .withMessage('Category must be between 2 and 50 characters'),
  body('description')
    .optional()
    .trim()
    .isLength({ max: 1000 })
    .withMessage('Description must not exceed 1000 characters'),
  handleValidationErrors
];

// Wishlist validation rules
export const validateWishlistItem = [
  body('productId')
    .isMongoId()
    .withMessage('Invalid product ID'),
  handleValidationErrors
];

// Price tracker validation rules
export const validateTrackerItem = [
  body('productId')
    .isMongoId()
    .withMessage('Invalid product ID'),
  body('targetPrice')
    .isFloat({ min: 0 })
    .withMessage('Target price must be a positive number'),
  handleValidationErrors
];

// Style advice validation rules
export const validateStyleAdvice = [
  body('gender')
    .isIn(['male', 'female'])
    .withMessage('Gender must be either male or female'),
  body('event')
    .isIn(['casual', 'formal', 'wedding', 'eid', 'jumma', 'party', 'office'])
    .withMessage('Please select a valid event type'),
  body('age')
    .optional()
    .isInt({ min: 1, max: 120 })
    .withMessage('Age must be between 1 and 120'),
  body('skin_tone')
    .optional()
    .isIn(['warm', 'cool', 'neutral'])
    .withMessage('Skin tone must be warm, cool, or neutral'),
  body('cultural_factors')
    .optional()
    .isIn(['desi', 'western', 'fusion'])
    .withMessage('Cultural factors must be desi, western, or fusion'),
  body('season')
    .optional()
    .isIn(['summer', 'winter', 'spring', 'fall', 'current'])
    .withMessage('Season must be summer, winter, spring, fall, or current'),
  body('face_shape')
    .optional()
    .isIn(['oval', 'round', 'square', 'heart', 'diamond'])
    .withMessage('Face shape must be oval, round, square, heart, or diamond'),
  body('hair_type')
    .optional()
    .isIn(['straight', 'wavy', 'curly'])
    .withMessage('Hair type must be straight, wavy, or curly'),
  handleValidationErrors
];
