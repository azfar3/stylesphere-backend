import mongoose from 'mongoose';
import bcrypt from 'bcryptjs';
import User from '../models/User.js';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const seedUsers = async () => {
  try {
    // Connect to MongoDB
    await mongoose.connect(process.env.MONGO_URI);

    console.log('Connected to MongoDB');

    // Clear existing users (optional - comment out if you want to keep existing users)
    // await User.deleteMany({});
    // console.log('Cleared existing users');

    // Hash password function
    const hashPassword = async (password) => {
      const saltRounds = 12;
      return await bcrypt.hash(password, saltRounds);
    };

    // Define users to seed
    const usersToSeed = [
      {
        name: 'Admin User',
        email: 'admin@stylesphere.com',
        password: await hashPassword('admin123'),
        role: 'admin',
        preferences: {
          theme: 'dark',
          notifications: true
        }
      },
      {
        name: 'Test User',
        email: 'test@stylesphere.com',
        password: await hashPassword('test123'),
        role: 'user',
        preferences: {
          theme: 'light',
          notifications: true
        }
      },
      {
        name: 'John Doe',
        email: 'john@example.com',
        password: await hashPassword('password123'),
        role: 'user',
        preferences: {
          theme: 'light',
          notifications: false
        }
      }
    ];

    // Check if users already exist and create only new ones
    for (const userData of usersToSeed) {
      const existingUser = await User.findOne({ email: userData.email });
      
      if (existingUser) {
        console.log(`User ${userData.email} already exists, skipping...`);
        continue;
      }

      const user = await User.create(userData);
      console.log(`[SUCCESS] Created ${user.role} user: ${user.email}`);
    }

    console.log('\n[SUCCESS] User seeding completed successfully!');
    console.log('\n[INFO] Login Credentials:');
    console.log('='.repeat(50));
    console.log('[ADMIN] ADMIN USER:');
    console.log('   Email: admin@stylesphere.com');
    console.log('   Password: admin123');
    console.log('');
    console.log('[TEST] TEST USER:');
    console.log('   Email: test@stylesphere.com');
    console.log('   Password: test123');
    console.log('');
    console.log('[DEMO] DEMO USER:');
    console.log('   Email: john@example.com');
    console.log('   Password: password123');
    console.log('='.repeat(50));

  } catch (error) {
    console.error('[ERROR] Error seeding users:', error);
  } finally {
    // Close database connection
    await mongoose.connection.close();
    console.log('\n[INFO] Database connection closed');
    process.exit(0);
  }
};

// Run the seed function
seedUsers();
