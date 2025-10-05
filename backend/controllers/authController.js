import User from '../models/User.js';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';

// Helper function to generate JWT token
const generateToken = (userId) => {
  return jwt.sign(
    { id: userId },
    process.env.JWT_SECRET,
    { 
      expiresIn: process.env.JWT_EXPIRES_IN || '30d',
      issuer: 'stylesphere-api',
      audience: 'stylesphere-client'
    }
  );
};

// Helper function to format user response
const formatUserResponse = (user) => {
  return {
    id: user._id,
    name: user.name,
    email: user.email,
    role: user.role || 'user',
    createdAt: user.createdAt,
    lastLoginAt: user.lastLoginAt,
    preferences: user.preferences || {}
  };
};

export const register = async (req, res, next) => {
  try {
    const { name, email, password } = req.body;
    
    // Check if user already exists
    const existingUser = await User.findOne({ 
      email: email.toLowerCase() 
    }).lean();
    
    if (existingUser) {
      return res.status(409).json({ 
        success: false,
        error: 'User with this email already exists'
      });
    }

    // Hash password
    const saltRounds = process.env.NODE_ENV === 'production' ? 12 : 10;
    const hashedPassword = await bcrypt.hash(password, saltRounds);
    
    // Create user
    const user = await User.create({ 
      name: name.trim(),
      email: email.toLowerCase().trim(),
      password: hashedPassword
    });

    // Generate token
    const token = generateToken(user._id);
    
    // Log successful registration (without sensitive data)
    console.log(`User registered: ${user.email} at ${new Date().toISOString()}`);
    
    res.status(201).json({ 
      success: true,
      message: 'User registered successfully',
      token,
      user: formatUserResponse(user)
    });
  } catch (error) {
    console.error('Registration error:', error);
    next(error);
  }
};

export const login = async (req, res, next) => {
  try {
    const { email, password } = req.body;
    
    // Basic validation
    if (!email || !password) {
      return res.status(400).json({ 
        success: false,
        error: 'Email and password are required'
      });
    }
    
    // Find user and include password for comparison
    const user = await User.findOne({ 
      email: email.toLowerCase().trim() 
    }).select('+password');
    
    if (!user) {
      console.warn(`Login attempt with non-existent email: ${email} at ${new Date().toISOString()}`);
      return res.status(401).json({ 
        success: false,
        error: 'Invalid email or password. Please check your credentials and try again.'
      });
    }

    // Check password
    const isPasswordValid = await bcrypt.compare(password, user.password);
    
    if (!isPasswordValid) {
      // Log failed login attempt
      console.warn(`Failed login attempt for ${email} at ${new Date().toISOString()}`);
      
      return res.status(401).json({ 
        success: false,
        error: 'Invalid email or password. Please check your credentials and try again.'
      });
    }

    // Update last login time
    await User.findByIdAndUpdate(user._id, { 
      lastLoginAt: new Date() 
    });

    // Generate token
    const token = generateToken(user._id);
    
    // Log successful login
    console.log(`[SUCCESS] User logged in: ${user.email} at ${new Date().toISOString()}`);
    
    res.json({ 
      success: true,
      message: 'Login successful! Welcome back.',
      token,
      user: formatUserResponse(user)
    });
  } catch (error) {
    console.error('[ERROR] Login error:', error);
    
    // Return user-friendly error
    res.status(500).json({
      success: false,
      error: 'An error occurred during login. Please try again later.'
    });
  }
};

export const getProfile = async (req, res, next) => {
  try {
    const user = await User.findById(req.user.id)
      .populate('wishlist', 'name price image')
      .lean();
    
    if (!user) {
      return res.status(404).json({ 
        success: false,
        error: 'User not found'
      });
    }
    
    res.json({ 
      success: true,
      user: formatUserResponse(user)
    });
  } catch (error) {
    console.error('Get profile error:', error);
    next(error);
  }
};

export const updateProfile = async (req, res, next) => {
  try {
    const { name, preferences } = req.body;
    const userId = req.user.id;
    
    const updateData = {};
    if (name) updateData.name = name.trim();
    if (preferences) updateData.preferences = preferences;
    
    const user = await User.findByIdAndUpdate(
      userId,
      updateData,
      { new: true, runValidators: true }
    ).lean();
    
    if (!user) {
      return res.status(404).json({ 
        success: false,
        error: 'User not found'
      });
    }
    
    res.json({ 
      success: true,
      message: 'Profile updated successfully',
      user: formatUserResponse(user)
    });
  } catch (error) {
    console.error('Update profile error:', error);
    next(error);
  }
};
