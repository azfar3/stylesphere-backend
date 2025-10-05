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

const router = express.Router();

// Public routes
router.post('/login', validateLogin, login);
router.post('/register', validateRegister, register);

// Protected routes
router.get('/profile', protect, getProfile);
router.put('/profile', protect, updateProfile);

export default router;
