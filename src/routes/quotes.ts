import express from 'express';
import { body } from 'express-validator';
import Quote from '../models/Quote';
import { authenticateToken, requireRole } from '../middleware/auth';
import { validateInput } from '../middleware/validation';

const router = express.Router();

// Get quotes (role-based filtering)
router.get('/', authenticateToken, async (req: any, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;

    let filter: any = {};
    if (req.user.role === 'vendor') {
      filter.vendorId = req.user._id;
    }

    const quotes = await Quote.find(filter)
      .populate('orderId', 'title category budget')
      .populate('vendorId', 'first_name last_name email company_name')
      .populate('reviewedBy', 'first_name last_name email')
      .sort({ submittedAt: -1 })
      .skip(skip)
      .limit(limit);

    const total = await Quote.countDocuments(filter);

    res.json({
      success: true,
      data: { quotes },
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

// Submit quote (Vendor only)
router.post('/', [
  authenticateToken,
  requireRole(['vendor']),
  body('orderId').isMongoId(),
  body('amount').isNumeric(),
  body('description').notEmpty().trim(),
  body('deliveryTime').notEmpty().trim()
], validateInput, async (req: any, res) => {
  try {
    const quote = new Quote({
      ...req.body,
      vendorId: req.user._id
    });

    await quote.save();
    await quote.populate('orderId', 'title category budget');

    res.status(201).json({
      success: true,
      message: 'Quote submitted successfully',
      data: { quote }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server error',
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Approve quote
router.put('/:id/approve', [
  authenticateToken,
  requireRole(['manager', 'staff'])
], async (req: any, res) => {
  try {
    const quote = await Quote.findByIdAndUpdate(
      req.params.id,
      {
        status: 'approved',
        reviewedAt: new Date(),
        reviewedBy: req.user._id
      },
      { new: true }
    ).populate('orderId', 'title category budget')
     .populate('vendorId', 'first_name last_name email company_name');

    if (!quote) {
      return res.status(404).json({
        success: false,
        message: 'Quote not found'
      });
    }

    res.json({
      success: true,
      message: 'Quote approved',
      data: { quote }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server error',
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Reject quote
router.put('/:id/reject', [
  authenticateToken,
  requireRole(['manager', 'staff'])
], async (req: any, res) => {
  try {
    const quote = await Quote.findByIdAndUpdate(
      req.params.id,
      {
        status: 'rejected',
        reviewedAt: new Date(),
        reviewedBy: req.user._id
      },
      { new: true }
    ).populate('orderId', 'title category budget')
     .populate('vendorId', 'first_name last_name email company_name');

    if (!quote) {
      return res.status(404).json({
        success: false,
        message: 'Quote not found'
      });
    }

    res.json({
      success: true,
      message: 'Quote rejected',
      data: { quote }
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