import mongoose from 'mongoose';

const connectDB = async () => {
  try {
    const mongoURI = process.env.MONGO_URI || 'mongodb://localhost:27017/stylesphere';
    
    console.log('Attempting to connect to MongoDB...');
    
    const conn = await mongoose.connect(mongoURI, {
      // Remove deprecated options, use only the essential ones
    });

    console.log(`[SUCCESS] MongoDB Connected: ${conn.connection.host}`);
    console.log(`[INFO] Database: ${conn.connection.name}`);
    
    // Handle connection events
    mongoose.connection.on('error', (err) => {
      console.error('[ERROR] MongoDB connection error:', err);
    });

    mongoose.connection.on('disconnected', () => {
      console.log('[WARNING] MongoDB disconnected');
    });

    mongoose.connection.on('reconnected', () => {
      console.log('[INFO] MongoDB reconnected');
    });

    // Graceful shutdown
    process.on('SIGINT', async () => {
      try {
        await mongoose.connection.close();
        console.log('[INFO] MongoDB connection closed through app termination');
        process.exit(0);
      } catch (error) {
        console.error('Error during graceful shutdown:', error);
        process.exit(1);
      }
    });

  } catch (error) {
    console.error('[ERROR] Database connection failed:', error.message);
    
    // In development, we can continue without DB, but log the error
    if (process.env.NODE_ENV === 'development') {
      console.warn('[WARNING] Running in development mode without database connection');
    } else {
      // In production, exit if can't connect to database
      process.exit(1);
    }
  }
};

export default connectDB;
