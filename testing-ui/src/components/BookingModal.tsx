import React, { useState } from 'react';
import { CheckCircle2, Copy, Database, Loader2, X } from 'lucide-react';
import { api } from '../api/client';
import { Booking } from '../types';

interface BookingModalProps {
  booking: Booking | null;
  onClose: () => void;
}

export const BookingModal: React.FC<BookingModalProps> = ({ booking, onClose }) => {
  const [copied, setCopied] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [verifiedRecord, setVerifiedRecord] = useState<Booking | null>(null);
  const [verifyError, setVerifyError] = useState<string | null>(null);

  if (!booking) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(booking.booking_reference);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleVerifyInDb = async () => {
    setVerifying(true);
    setVerifyError(null);
    try {
      const record = await api.getBooking(booking.booking_reference);
      setVerifiedRecord(record);
    } catch (err: any) {
      setVerifyError(err.message || 'Lookup failed');
    } finally {
      setVerifying(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title">
            <CheckCircle2 size={22} className="text-accent" />
            <h3>Ride Booking Confirmed</h3>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          <div className="reference-card">
            <span className="ref-label">Booking Reference Code</span>
            <div className="ref-value-row">
              <span className="ref-code">{booking.booking_reference}</span>
              <button className="copy-btn" onClick={handleCopy} title="Copy Reference">
                <Copy size={15} />
                <span>{copied ? 'Copied!' : 'Copy'}</span>
              </button>
            </div>
          </div>

          <div className="booking-meta-grid">
            <div className="meta-item">
              <span className="meta-label">Status</span>
              <span className="meta-value status-badge confirmed">
                {booking.booking_status.toUpperCase()}
              </span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Provider</span>
              <span className="meta-value">{booking.provider}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Booking ID</span>
              <span className="meta-value code-sm">{booking.id}</span>
            </div>
            {booking.recommendation_id && (
              <div className="meta-item">
                <span className="meta-label">Recommendation ID</span>
                <span className="meta-value code-sm">{booking.recommendation_id}</span>
              </div>
            )}
            {booking.booked_at && (
              <div className="meta-item full-width">
                <span className="meta-label">Booked At</span>
                <span className="meta-value">{new Date(booking.booked_at).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })} IST</span>
              </div>
            )}
          </div>

          <div className="verify-section">
            <button
              className="verify-btn"
              onClick={handleVerifyInDb}
              disabled={verifying}
            >
              {verifying ? (
                <>
                  <Loader2 size={15} className="spin" />
                  <span>Querying GET /api/v1/bookings/{booking.booking_reference}...</span>
                </>
              ) : (
                <>
                  <Database size={15} />
                  <span>Verify Record via GET /api/v1/bookings/{booking.booking_reference}</span>
                </>
              )}
            </button>

            {verifyError && (
              <div className="verify-error">
                Failed to verify booking: {verifyError}
              </div>
            )}

            {verifiedRecord && (
              <div className="verified-result">
                <div className="verified-badge">
                  <CheckCircle2 size={14} className="text-accent" />
                  <span>Verified Live in Database (HTTP 200)</span>
                </div>
                <pre className="json-preview">
                  {JSON.stringify(verifiedRecord, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>

        <div className="modal-footer">
          <button className="primary-btn full" onClick={onClose}>
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
