import React, { useEffect, useState } from 'react';
import { CalendarCheck, Car, CheckCircle2, Clock, Loader2, Zap } from 'lucide-react';
import { api } from '../api/client';
import { Booking, RideOption } from '../types';
import { formatINR } from '../utils/india';

interface RecommendationCardProps {
  recommendationId?: string | null;
  options?: RideOption[];
  onBook: (recommendationId: string, tier: string) => Promise<Booking>;
  onViewBooking: (booking: Booking) => void;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({
  recommendationId,
  options: providedOptions,
  onBook,
  onViewBooking,
}) => {
  const [bookingTier, setBookingTier] = useState<string | null>(null);
  const [confirmedBookings, setConfirmedBookings] = useState<Record<string, Booking>>({});
  const [error, setError] = useState<string | null>(null);
  const [options, setOptions] = useState<RideOption[]>(providedOptions ?? []);

  // Admin console: load the REAL persisted quote (INR, demo-flagged) instead of
  // showing hardcoded placeholder prices.
  useEffect(() => {
    if (providedOptions || !recommendationId) return;
    api
      .getRecommendation(recommendationId)
      .then(rec =>
        setOptions(
          (rec.recommendation_data.options ?? []).map(o => ({
            tier: o.tier,
            label: `${o.label}${o.is_demo ? ' (DEMO)' : ''}`,
            estimated_price: o.fare_inr,
            eta_minutes: o.trip_minutes,
          }))
        )
      )
      .catch(() => setError('Could not load quote for this recommendation.'));
  }, [recommendationId, providedOptions]);

  const handleBook = async (opt: RideOption) => {
    if (!recommendationId) {
      setError('No recommendation ID associated with this turn.');
      return;
    }

    setBookingTier(opt.tier);
    setError(null);

    try {
      const booking = await onBook(recommendationId, opt.tier);
      setConfirmedBookings(prev => ({ ...prev, [opt.tier]: booking }));
      onViewBooking(booking);
    } catch (err: any) {
      setError(err.message || 'Failed to book ride');
    } finally {
      setBookingTier(null);
    }
  };

  return (
    <div className="recommendation-container">
      <div className="rec-header">
        <div className="rec-title">
          <Zap size={16} className="text-accent" />
          <span>Available Ride Options</span>
        </div>
        {recommendationId && (
          <span className="rec-id-badge" title="Recommendation ID">
            ID: {recommendationId.slice(0, 8)}...
          </span>
        )}
      </div>

      {error && <div className="rec-error-banner">{error}</div>}

      <div className="rec-cards-grid">
        {options.map((opt, idx) => {
          const isConfirmed = !!confirmedBookings[opt.tier];
          const booking = confirmedBookings[opt.tier];
          const isBooking = bookingTier === opt.tier;

          return (
            <div
              key={idx}
              className={`rec-card ${isConfirmed ? 'confirmed' : ''}`}
            >
              <div className="rec-card-top">
                <div className="rec-card-tier">
                  <Car size={20} className="rec-car-icon" />
                  <span className="tier-name">{opt.label ?? opt.tier}</span>
                </div>
                <div className="rec-card-price">
                  <span>{formatINR(opt.estimated_price)}</span>
                </div>
              </div>

              <div className="rec-card-details">
                <span className="detail-item">
                  <Clock size={13} />
                  <span>Trip: ~{opt.eta_minutes} min</span>
                </span>
                <span className="detail-item provider-tag">
                  Demo provider
                </span>
              </div>

              <div className="rec-card-action">
                {isConfirmed ? (
                  <button
                    className="booked-btn"
                    onClick={() => onViewBooking(booking)}
                  >
                    <CheckCircle2 size={15} />
                    <span>{booking.booking_reference} (Confirmed)</span>
                  </button>
                ) : (
                  <button
                    className="book-btn"
                    disabled={isBooking || !recommendationId}
                    onClick={() => handleBook(opt)}
                  >
                    {isBooking ? (
                      <>
                        <Loader2 size={15} className="spin" />
                        <span>Reserving...</span>
                      </>
                    ) : (
                      <>
                        <CalendarCheck size={15} />
                        <span>Book This Ride</span>
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
