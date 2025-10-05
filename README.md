# StyleSphere - Full Stack Fashion Platform

A modern, optimized full-stack fashion e-commerce platform built with React, Node.js, Express, and MongoDB.

## 🚀 Features

### Frontend (React)
- **Modern React Architecture**: Lazy loading, code splitting, and optimized rendering
- **Authentication System**: JWT-based authentication with protected routes
- **Performance Optimizations**: 
  - React.memo for component optimization
  - Virtual scrolling for large lists
  - Lazy image loading
  - Code splitting with React.lazy
- **UI/UX**: Ant Design components with responsive design
- **Error Handling**: Error boundaries and comprehensive error management

### Backend (Node.js/Express)
- **Security First**: Helmet, CORS, rate limiting, and input validation
- **Performance**: Compression, caching, and optimized database queries
- **Authentication**: JWT with refresh tokens and secure password hashing
- **API Design**: RESTful APIs with consistent response formats
- **Error Handling**: Centralized error handling middleware
- **Logging**: Morgan for request logging and custom application logs

### Database (MongoDB)
- **Mongoose ODM**: Schema validation and relationship management
- **Optimized Queries**: Lean queries, proper indexing, and population strategies

## 🛠️ Tech Stack

**Frontend:**
- React 19.1.0
- React Router DOM 7.6.3
- Ant Design 5.26.3
- Axios 1.7.9
- React Window (Virtual scrolling)

**Backend:**
- Node.js with Express 5.1.0
- MongoDB with Mongoose 8.17.1
- JWT Authentication
- bcryptjs for password hashing
- express-validator for input validation
- helmet, compression, morgan for security and performance

**Development Tools:**
- Concurrently for running both servers
- Nodemon for backend auto-restart
- ESLint and Prettier for code quality

## 📦 Installation & Setup

### Prerequisites
- Node.js (v16 or higher)
- MongoDB (local or cloud)
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd stylesphere
   ```

2. **Install all dependencies**
   ```bash
   npm install
   npm run install:all
   ```

3. **Environment Setup**
   
   **Backend (.env):**
   ```env
   PORT=5000
   MONGO_URI=mongodb://localhost:27017/stylesphere
   JWT_SECRET=your_super_secret_jwt_key_here
   JWT_EXPIRES_IN=30d
   NODE_ENV=development
   ```

   **Frontend (.env):**
   ```env
   REACT_APP_API_URL=http://localhost:5000/api
   REACT_APP_ENV=development
   REACT_APP_APP_NAME=StyleSphere
   ```

4. **Start Development Servers**
   ```bash
   # Run both frontend and backend concurrently
   npm run dev
   
   # Or run separately
   npm run backend:dev    # Backend only
   npm run frontend:dev   # Frontend only
   ```

5. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - Health Check: http://localhost:5000/health

## 🏗️ Project Structure

```
stylesphere/
├── backend/
│   ├── config/
│   │   └── db.js                 # Database connection
│   ├── controllers/
│   │   ├── authController.js     # Authentication logic
│   │   ├── productController.js  # Product operations
│   │   └── ...
│   ├── middleware/
│   │   ├── authMiddleware.js     # JWT verification
│   │   ├── errorMiddleware.js    # Error handling
│   │   └── validationMiddleware.js # Input validation
│   ├── models/
│   │   ├── User.js              # User schema
│   │   ├── Product.js           # Product schema
│   │   └── ...
│   ├── routes/
│   │   ├── authRoutes.js        # Auth endpoints
│   │   └── ...
│   ├── utils/
│   ├── .env                     # Environment variables
│   ├── package.json
│   └── server.js               # Express server setup
├── stylesphere-frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ErrorBoundary.jsx
│   │   │   ├── ProductCard.jsx
│   │   │   ├── ProtectedRoute.jsx
│   │   │   └── VirtualList.jsx
│   │   ├── contexts/
│   │   │   └── AuthContext.js   # Authentication context
│   │   ├── pages/
│   │   ├── services/
│   │   │   └── api.js           # API service layer
│   │   ├── styles/
│   │   └── App.jsx             # Main app component
│   ├── .env                    # Frontend environment
│   └── package.json
├── package.json               # Root package.json
└── README.md
```

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile (protected)
- `PUT /api/auth/profile` - Update user profile (protected)

### Products
- `GET /api/products` - Get all products
- `GET /api/products/:id` - Get product by ID
- `GET /api/products/search` - Search products

### Wishlist
- `GET /api/wishlist` - Get user wishlist (protected)
- `POST /api/wishlist/add` - Add to wishlist (protected)
- `DELETE /api/wishlist/:id` - Remove from wishlist (protected)

### Price Tracker
- `GET /api/tracker` - Get tracked products (protected)
- `POST /api/tracker/add` - Add product to tracker (protected)
- `DELETE /api/tracker/:id` - Remove from tracker (protected)

### Style Advisor
- `POST /api/advisor/advice` - Get style advice (protected)
- `POST /api/advisor/outfits` - Get outfit recommendations (protected)

## 🚀 Performance Optimizations

### Frontend Optimizations
1. **Code Splitting**: Components are lazy-loaded using React.lazy()
2. **Virtual Scrolling**: Large lists use react-window for performance
3. **Memoization**: Components wrapped with React.memo to prevent unnecessary re-renders
4. **Image Optimization**: Lazy loading and error handling for images
5. **Bundle Optimization**: Tree shaking and code splitting reduce bundle size

### Backend Optimizations
1. **Security**: Helmet for security headers, rate limiting, CORS configuration
2. **Performance**: Compression middleware, optimized MongoDB queries
3. **Caching**: Database query optimization with lean() queries
4. **Error Handling**: Centralized error handling with proper logging
5. **Validation**: Input validation with express-validator

### Database Optimizations
1. **Indexing**: Proper indexes on frequently queried fields
2. **Lean Queries**: Using .lean() for read-only operations
3. **Population**: Selective field population to reduce data transfer
4. **Connection Pooling**: Optimized MongoDB connection settings

## 🛡️ Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcryptjs with proper salt rounds
- **Rate Limiting**: Protection against brute force attacks
- **Input Validation**: Comprehensive validation with express-validator
- **Security Headers**: Helmet.js for security headers
- **CORS**: Properly configured CORS policies
- **Error Handling**: Secure error responses without exposing sensitive data

## 📱 Development

### Available Scripts

**Root Level:**
- `npm run dev` - Run both frontend and backend
- `npm run install:all` - Install all dependencies
- `npm run build` - Build frontend for production
- `npm start` - Start production server

**Backend:**
- `npm run dev` - Start with nodemon
- `npm start` - Start production server

**Frontend:**
- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests

### Code Quality
- ESLint configuration for consistent code style
- Error boundaries for graceful error handling
- TypeScript-ready structure
- Comprehensive error logging

## 🚀 Deployment

### Production Build
```bash
# Build frontend
npm run build

# Set production environment
NODE_ENV=production

# Start production server
npm start
```

### Environment Variables for Production
Update your production environment variables:
- Set `NODE_ENV=production`
- Use secure JWT secrets
- Configure production MongoDB URI
- Set proper CORS origins
- Enable production logging

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:
1. Check the existing issues on GitHub
2. Create a new issue with detailed information
3. Include environment details and error logs

---

**Built with ❤️ for the fashion community**
