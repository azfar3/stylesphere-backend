import User from '../models/User.js';

// Middleware to check if user is an admin
export const requireAdmin = async (req, res, next) => {
  try {
    // First check if user is authenticated (should be called after protect middleware)
    if (!req.user || !req.user.id) {
      return res.status(401).json({
        success: false,
        error: 'Authentication required'
      });
    }

    // Get user from database to check role
    const user = await User.findById(req.user.id).select('role').lean();
    
    if (!user) {
      return res.status(404).json({
        success: false,
        error: 'User not found'
      });
    }

    // Check if user is admin
    if (user.role !== 'admin') {
      return res.status(403).json({
        success: false,
        error: 'Admin access required'
      });
    }

    // User is admin, proceed to next middleware/route
    next();
  } catch (error) {
    console.error('Admin middleware error:', error);
    res.status(500).json({
      success: false,
      error: 'Server error during authorization check'
    });
  }
};

// Middleware to check if user is admin or the resource owner
export const requireAdminOrOwner = (resourceUserIdPath = 'user') => {
  return async (req, res, next) => {
    try {
      // Check if user is authenticated
      if (!req.user || !req.user.id) {
        return res.status(401).json({
          success: false,
          error: 'Authentication required'
        });
      }

      // Get user from database to check role
      const user = await User.findById(req.user.id).select('role').lean();
      
      if (!user) {
        return res.status(404).json({
          success: false,
          error: 'User not found'
        });
      }

      // If user is admin, allow access
      if (user.role === 'admin') {
        return next();
      }

      // If not admin, check if user owns the resource
      const resourceUserId = req.params[resourceUserIdPath] || req.body[resourceUserIdPath];
      
      if (req.user.id !== resourceUserId) {
        return res.status(403).json({
          success: false,
          error: 'Access denied. You can only access your own resources.'
        });
      }

      // User owns the resource, proceed
      next();
    } catch (error) {
      console.error('Admin or owner middleware error:', error);
      res.status(500).json({
        success: false,
        error: 'Server error during authorization check'
      });
    }
  };
};

export default {
  requireAdmin,
  requireAdminOrOwner
};
