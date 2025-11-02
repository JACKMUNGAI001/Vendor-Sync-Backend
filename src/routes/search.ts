import express from 'express';
import Order from '../models/Order';
import User from '../models/User';
import Quote from '../models/Quote';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Global search
router.get('/', authenticateToken, async (req, res) => {
  try {
    const { q } = req.query;
    
    if (!q) {
      return res.status(400).json({
        success: false,
        message: 'Search query is required'
      });
    }

    const searchRegex = new RegExp(q as string, 'i');

    const [orders, vendors, quotes] = await Promise.all([
      Order.find({
        $or: [
          { title: searchRegex },
          { description: searchRegex },
          { category: searchRegex }
        ]
      }).populate('createdBy', 'first_name last_name').limit(10),

      User.find({
        role: 'vendor',
        isActive: true,
        $or: [
          { first_name: searchRegex },
          { last_name: searchRegex },
          { company_name: searchRegex }
        ]
      }).select('-password').limit(10),

      Quote.find({
        description: searchRegex
      }).populate('orderId', 'title').populate('vendorId', 'first_name last_name company_name').limit(10)
    ]);

    res.json({
      success: true,
      data: {
        orders,
        vendors,
        quotes
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

export default router;