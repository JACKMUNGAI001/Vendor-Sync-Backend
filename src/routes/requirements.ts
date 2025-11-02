import express from 'express';
import { body } from 'express-validator';
import Requirement from '../models/Requirement';
import { authenticateToken, requireRole } from '../middleware/auth';
import { validateInput } from '../middleware/validation';

const router = express.Router();

// Get requirements
router.get('/', authenticateToken, async (req, res) => {
  try {
    const page = parseInt(req.query.page as string) || 1;
    const limit = parseInt(req.query.limit as string) || 10;
    const skip = (page - 1) * limit;

    const requirements = await Requirement.find()
      .populate('createdBy', 'first_name last_name email')
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit);

    const total = await Requirement.countDocuments();

    res.json({
      success: true,
      data: { requirements },
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

// Create requirement
router.post('/', [
  authenticateToken,
  requireRole(['manager', 'staff']),
  body('title').notEmpty().trim(),
  body('description').notEmpty().trim(),
  body('category').notEmpty().trim()
], validateInput, async (req: any, res) => {
  try {
    const requirement = new Requirement({
      ...req.body,
      createdBy: req.user._id
    });

    await requirement.save();
    await requirement.populate('createdBy', 'first_name last_name email');

    res.status(201).json({
      success: true,
      message: 'Requirement created successfully',
      data: { requirement }
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