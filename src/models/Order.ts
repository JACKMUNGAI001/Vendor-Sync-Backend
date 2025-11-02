import mongoose, { Document, Schema } from 'mongoose';

export interface IOrder extends Document {
  title: string;
  description: string;
  category: string;
  budget: number;
  deadline: Date;
  priority: 'low' | 'medium' | 'high';
  status: 'pending' | 'in-progress' | 'completed' | 'cancelled';
  createdBy: mongoose.Types.ObjectId;
  assignedVendors: mongoose.Types.ObjectId[];
  createdAt: Date;
  updatedAt: Date;
}

const orderSchema = new Schema<IOrder>({
  title: { type: String, required: true },
  description: { type: String, required: true },
  category: { type: String, required: true },
  budget: { type: Number, required: true },
  deadline: { type: Date, required: true },
  priority: { type: String, enum: ['low', 'medium', 'high'], required: true },
  status: { type: String, enum: ['pending', 'in-progress', 'completed', 'cancelled'], default: 'pending' },
  createdBy: { type: Schema.Types.ObjectId, ref: 'User', required: true },
  assignedVendors: [{ type: Schema.Types.ObjectId, ref: 'User' }]
}, { timestamps: true });

export default mongoose.model<IOrder>('Order', orderSchema);