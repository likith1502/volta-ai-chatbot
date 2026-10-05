import React from 'react';
import { AlertTriangle, Car, CheckCircle2, Clock, MapPin, Users, XCircle } from 'lucide-react';
import { RideState } from '../types';
import { formatINR } from '../utils/india';

interface RideCardProps {
  ride: RideState;
  /** True only for the newest ride card: older cards become read-only. */
  isLatest: boolean;
  disabled: boolean;
  onSend: (text: string) => void;
}

/**
 * Customer ride card. It never books directly: every action is sent as a chat
 * message, so the backend's "select vehicle -> explicit yes" rules always apply.
 */
export const RideCard: React.FC<RideCardProps> = ({ ride, isLatest, disabled, onSend }) => {
  const { stage, pickup, drop, options, selected_tier, booking, is_demo } = ride;
  if (!pickup && !drop && !booking) return null;

  const interactive = isLatest && !disabled;
  const selected = options.find(o => o.tier === selected_tier);

  return (
    <div className="ride-card">
      {(pickup || drop) && (
        <div className="ride-route">
          <div className="ride-route-row">
            <span className="ride-dot ride-dot--pickup" />
            <span className="ride-route-label">Pickup</span>
            <span className="ride-route-value">{pickup ? pickup.name : 'Not set yet'}</span>
          </div>
          <div className="ride-route-row">
            <MapPin size={12} className="ride-pin" />
            <span className="ride-route-label">Drop</span>
            <span className="ride-route-value">{drop ? drop.name : 'Not set yet'}</span>
          </div>
        </div>
      )}

      {options.length > 0 && stage !== 'booked' && (
        <div className="ride-options">
          {options.map(o => {
            const isSel = o.tier === selected_tier;
            return (
              <button
                key={o.tier}
                className={`ride-option ${isSel ? 'ride-option--selected' : ''}`}
                disabled={!interactive}
                onClick={() => onSend(o.label)}
                aria-pressed={isSel}
              >
                <Car size={18} />
                <span className="ride-option-name">{o.label}</span>
                <span className="ride-option-meta">
                  <Users size={11} /> {o.seats}
                  <Clock size={11} /> ~{o.trip_minutes} min
                </span>
                <span className="ride-option-fare">{formatINR(o.fare_inr)}</span>
              </button>
            );
          })}
        </div>
      )}

      {stage === 'confirming' && selected && interactive && (
        <div className="ride-confirm">
          <button className="ride-btn ride-btn--primary" onClick={() => onSend('Yes, book it')}>
            <CheckCircle2 size={15} /> Confirm {selected.label} · {formatINR(selected.fare_inr)}
          </button>
          <button className="ride-btn" onClick={() => onSend('No')}>
            Change
          </button>
        </div>
      )}

      {booking && (
        <div className={`ride-booking ${booking.status === 'cancelled' ? 'ride-booking--cancelled' : ''}`}>
          {booking.status === 'cancelled' ? <XCircle size={16} /> : <CheckCircle2 size={16} />}
          <div>
            <div className="ride-booking-ref">{booking.reference}</div>
            <div className="ride-booking-status">
              {booking.status.toUpperCase()}
              {booking.fare_inr != null && ` · ${formatINR(booking.fare_inr)}`}
            </div>
          </div>
          {booking.status !== 'cancelled' && interactive && (
            <button className="ride-btn ride-btn--danger" onClick={() => onSend('Cancel my ride')}>
              Cancel ride
            </button>
          )}
        </div>
      )}

      {is_demo && (
        <div className="ride-demo">
          <AlertTriangle size={12} />
          {booking
            ? 'Demo booking: no real cab is dispatched and no payment is taken.'
            : 'Demo prices: estimates only, not live VOLTA fares.'}
        </div>
      )}
    </div>
  );
};
