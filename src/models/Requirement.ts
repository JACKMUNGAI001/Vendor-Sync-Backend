import mongoose, { Document, Schema } from 'mongoose';

export interface IRequirement extends Document {
  title: string;
  description: string;
  category: string;
  priority: 'low' | 'medium' | 'high';
  status: 'active' | 'completed' | 'cancelled';
  createdBy: mongoose.Types.ObjectId;
  createdAt: Date;
}

const requirementSchema = new Schema<IRequirement>({
  title: { type: String, required: true },
  description: { type: String, required: true },
  category: { type: String, required: true },
  priority: { type: String, enum: ['low', 'medium', 'high'], default: 'medium' },
  status: { type: String, enum: ['active', 'completed', 'cancelled'], default: 'active' },
  createdBy: { type: Schema.Types.ObjectId, ref: 'User', required: true }
}, { timestamps: true });

export default mongoose.model<IRequirement>('Requirement', requirementSchema);