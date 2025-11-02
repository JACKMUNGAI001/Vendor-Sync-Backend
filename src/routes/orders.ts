import express from 'express';
import { body } from 'express-validator';
import Order from '../models/Order';
import { authenticateToken, requireRole } from '../middleware/auth';
import { validateInput } from '../middleware/validation';

const router = express.Router();

// Get orders (role-based filtering)
router.get('/', authenticateToken, async (req: any, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;

    let filter: any = {};
    if (req.user.role === 'vendor') {
      filter.assignedVendors = req.user._id;
    }

    const orders = await Order.find(filter)
      .populate('createdBy', 'first_name last_name email')
      .populate('assignedVendors', 'first_name last_name email company_name')
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit);

    const total = await Order.countDocuments(filter);

    res.json({
      success: true,
      data: { orders },
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit)
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

// Create order
router.post('/', [
  authenticateToken,
  requireRole(['manager', 'staff']),
  body('title').notEmpty().trim(),
  body('description').notEmpty().trim(),
  body('category').notEmpty().trim(),
  body('budget').isNumeric(),
  body('deadline').isISO8601(),
  body('priority').isIn(['low', 'medium', 'high'])
], validateInput, async (req: any, res) => {
  try {
    const order = new Order({
      ...req.body,
      createdBy: req.user._id
    });

    await order.save();
    await order.populate('createdBy', 'first_name last_name email');

    res.status(201).json({
      success: true,
      message: 'Order created successfully',
      data: { order }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server error',
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Get order by ID
router.get('/:id', authenticateToken, async (req: any, res) => {
  try {
    const order = await Order.findById(req.params.id)
      .populate('createdBy', 'first_name last_name email')
      .populate('assignedVendors', 'first_name last_name email company_name');

    if (!order) {
      return res.status(404).json({
        success: false,
        message: 'Order not found'
      });
    }

    res.json({
      success: true,
      data: { order }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server error',
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Update order status
router.put('/:id/status', [
  authenticateToken,
  requireRole(['manager', 'staff']),
  body('status').isIn(['pending', 'in-progress', 'completed', 'cancelled'])
], validateInput, async (req, res) => {
  try {
    const order = await Order.findByIdAndUpdate(
      req.params.id,
      { status: req.body.status },
      { new: true }
    ).populate('createdBy', 'first_name last_name email');

    if (!order) {
      return res.status(404).json({
        success: false,
        message: 'Order not found'
      });
    }

    res.json({
      success: true,
      message: 'Order status updated',
      data: { order }
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