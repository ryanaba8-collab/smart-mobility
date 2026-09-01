function TripDetail({ trip, loading, onClose }) {
  if (loading) {
    return <p>Chargement du trajet...</p>;
  }

  if (!trip) {
    return null;
  }

  function formatDuration(minutes) {
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;

    if (hours === 0) {
      return `${remainingMinutes} min`;
    }

    if (remainingMinutes === 0) {
      return `${hours} h`;
    }

    return `${hours} h ${remainingMinutes
      .toString()
      .padStart(2, "0")}`;
  }

  return (
  <div className="modal-overlay" onClick={onClose}>
    <section
      className="trip-modal"
      onClick={(event) => event.stopPropagation()}
    >
      <div className="modal-header">
        <div>
          <h2>Détail du trajet</h2>
          <p>Train {trip.train_number}</p>
        </div>

        <button
          type="button"
          className="modal-close"
          onClick={onClose}
          aria-label="Fermer"
        >
          ×
        </button>
      </div>

      <p>
        <strong>Ligne :</strong>{" "}
        {trip.route?.short_name || "—"}
        {trip.route?.long_name && (
          <> — {trip.route.long_name}</>
        )}
      </p>

      <div className="trip-summary">
        <div>
          <span>Départ</span>
          <strong>{trip.departure_time}</strong>
          <p>{trip.departure_station}</p>
        </div>

        <div className="trip-summary-arrow">
          →
        </div>

        <div>
          <span>Destination finale</span>
          <strong>{trip.arrival_time}</strong>
          <p>{trip.arrival_station}</p>
        </div>
      </div>

      <p>
        <strong>Durée totale :</strong>{" "}
        {formatDuration(trip.duration_minutes)}
      </p>

      <h3>Arrêts</h3>

      <ol className="trip-stops">
        {trip.stops.map((stop) => (
          <li
            key={`${stop.station_external_id}-${stop.stop_sequence}`}
          >
            <strong>{stop.station}</strong>

            <div>
              Arrivée : {stop.arrival_time}
              {" — "}
              Départ : {stop.departure_time}
            </div>
          </li>
        ))}
      </ol>
    </section>
  </div>
);
}

export default TripDetail;