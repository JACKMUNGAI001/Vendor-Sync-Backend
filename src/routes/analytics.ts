import express from 'express';
import Order from '../models/Order';
import Quote from '../models/Quote';
import User from '../models/User';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Dashboard analytics
router.get('/dashboard', authenticateToken, async (req: any, res) => {
  try {
    let stats: any = {};

    if (req.user.role === 'manager' || req.user.role === 'staff') {
      // Manager/Staff dashboard
      const [totalOrders, pendingOrders, totalVendors, totalQuotes] = await Promise.all([
        Order.countDocuments(),
        Order.countDocuments({ status: 'pending' }),
        User.countDocuments({ role: 'vendor', isActive: true }),
        Quote.countDocuments()
      ]);

      stats = {
        totalOrders,
        pendingOrders,
        totalVendors,
        totalQuotes
      };
    } else if (req.user.role === 'vendor') {
      // Vendor dashboard
      const [assignedOrders, submittedQuotes, approvedQuotes] = await Promise.all([
        Order.countDocuments({ assignedVendors: req.user._id }),
        Quote.countDocuments({ vendorId: req.user._id }),
        Quote.countDocuments({ vendorId: req.user._id, status: 'approved' })
      ]);

      stats = {
        assignedOrders,
        submittedQuotes,
        approvedQuotes
      };
    }

    res.json({
      success: true,
      data: { stats }
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