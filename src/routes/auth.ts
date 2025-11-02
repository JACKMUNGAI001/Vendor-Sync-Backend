import express from 'express';
import { body } from 'express-validator';
import jwt from 'jsonwebtoken';
import User from '../models/User';
import { validateInput } from '../middleware/validation';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Register
router.post('/register', [
  body('email').isEmail().normalizeEmail(),
  body('password').isLength({ min: 6 }),
  body('first_name').notEmpty().trim(),
  body('last_name').notEmpty().trim(),
  body('role').isIn(['manager', 'staff', 'vendor'])
], validateInput, async (req, res) => {
  try {
    const { email, password, first_name, last_name, role, phone, company_name } = req.body;

    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({
        success: false,
        message: 'User already exists'
      });
    }

    const user = new User({
      email,
      password,
      first_name,
      last_name,
      role,
      phone,
      company_name
    });

    await user.save();

    res.status(201).json({
      success: true,
      message: 'User created successfully',
      data: {
        user: {
          id: user._id,
          email: user.email,
          role: user.role
        }
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server error',
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Login
router.post('/login', [
  body('email').isEmail().normalizeEmail(),
  body('password').notEmpty()
], validateInput, async (req, res) => {
  try {
    const { email, password } = req.body;

    const user = await User.findOne({ email, isActive: true });
    if (!user || !(await user.comparePassword(password))) {
      return res.status(401).json({
        success: false,
        message: 'Invalid email or password'
      });
    }

    const token = jwt.sign(
      { userId: user._id, role: user.role },
      process.env.JWT_SECRET!,
      { expiresIn: process.env.JWT_EXPIRE }
    );

    res.json({
      success: true,
      message: 'Login successful',
      data: {
        token,
        user: {
          id: user._id,
          email: user.email,
          role: user.role,
          name: `${user.first_name} ${user.last_name}`,
          first_name: user.first_name,
          last_name: user.last_name
        }
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server error',
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Get current user
router.get('/me', authenticateToken, async (req: any, res) => {
  res.json({
    success: true,
    data: {
      user: {
        id: req.user._id,
        email: req.user.email,
        role: req.user.role,
        name: `${req.user.first_name} ${req.user.last_name}`,
        first_name: req.user.first_name,
        last_name: req.user.last_name,
        phone: req.user.phone,
        company_name: req.user.company_name
      }
    }
  });
});

export default router;