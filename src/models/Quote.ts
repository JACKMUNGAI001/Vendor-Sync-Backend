import mongoose, { Document, Schema } from 'mongoose';

export interface IQuote extends Document {
  orderId: mongoose.Types.ObjectId;
  vendorId: mongoose.Types.ObjectId;
  amount: number;
  description: string;
  deliveryTime: string;
  status: 'pending' | 'approved' | 'rejected';
  submittedAt: Date;
  reviewedAt?: Date;
  reviewedBy?: mongoose.Types.ObjectId;
}

const quoteSchema = new Schema<IQuote>({
  orderId: { type: Schema.Types.ObjectId, ref: 'Order', required: true },
  vendorId: { type: Schema.Types.ObjectId, ref: 'User', required: true },
  amount: { type: Number, required: true },
  description: { type: String, required: true },
  deliveryTime: { type: String, required: true },
  status: { type: String, enum: ['pending', 'approved', 'rejected'], default: 'pending' },
  submittedAt: { type: Date, default: Date.now },
  reviewedAt: Date,
  reviewedBy: { type: Schema.Types.ObjectId, ref: 'User' }
});

export default mongoose.model<IQuote>('Quote', quoteSchema);