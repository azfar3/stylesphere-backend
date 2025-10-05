import jwt from 'jsonwebtoken';
import User from '../models/User.js';

export const protect = async (req, res, next) => {
  try {
    let token = req.headers.authorization.split(' ')[1];

    console.log("token: ",token);
    

    // if (req.headers.authorization?.startsWith('Bearer')) {
    //   token = req.headers.authorization.split(' ')[1];
    // }

    if (!token) {
      return res.status(401).json({
        success: false,
        error: 'Not authorized to access this route'
      });
    }

    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET);

      const user = await User.findById(decoded.id).lean();

      if (!user) {
        return res.status(401).json({
          success: false,
          error: 'User no longer exists'
        });
      }

      req.user = { id: user._id, email: user.email, name: user.name };
      next();
    } catch (error) {
      console.error('Token verification failed:', error.message);

      let errorMessage = 'Invalid token';
      if (error.name === 'TokenExpiredError') {
        errorMessage = 'Token expired';
      } else if (error.name === 'JsonWebTokenError') {
        errorMessage = 'Invalid token';
      }

      return res.status(401).json({
        success: false,
        error: errorMessage
      });
    }
  } catch (error) {
    console.error('Auth middleware error:', error);
    return res.status(500).json({
      success: false,
      error: 'Server error'
    });
  }
};

export const optionalAuth = async (req, res, next) => {
  try {
    const token = req.headers.authorization?.split(' ')[1];

    if (token) {
      try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        const user = await User.findById(decoded.id).lean();

        if (user) {
          req.user = { id: user._id, email: user.email, name: user.name };
        }
      } catch (error) {
        console.warn('Optional auth failed:', error.message);
      }
    }

    next();
  } catch (error) {
    next();
  }
};

export default protect;
