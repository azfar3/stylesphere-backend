import express from 'express';
import { 
  login, 
  register, 
  getProfile, 
  updateProfile 
} from '../controllers/authController.js';
import { 
  validateLogin, 
  validateRegister 
} from '../middleware/validationMiddleware.js';
import { protect } from '../middleware/authMiddleware.js';
import { authLimiter } from '../middleware/rateLimitMiddleware.js';

const router = express.Router();

// Public routes
router.post('/login', authLimiter, validateLogin, login);
router.post('/register', authLimiter, validateRegister, register);


// Protected routes
router.get('/profile', protect, getProfile);
router.put('/profile', protect, updateProfile);

export default router;
