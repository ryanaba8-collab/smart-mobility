function TripList({ trips, searched, loading, onTripDetail }) {
  if (loading) {
    return <p>Recherche en cours...</p>;
  }

  if (!searched) {
    return null;
  }

  function formatTime(datetime) {
    return new Date(datetime).toLocaleTimeString("fr-FR", {
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  function getDuration(departureDatetime, arrivalDatetime) {
    const departure = new Date(departureDatetime);
    const arrival = new Date(arrivalDatetime);

    const durationMinutes = Math.round(
      (arrival - departure) / (1000 * 60)
    );

    const hours = Math.floor(durationMinutes / 60);
    const minutes = durationMinutes % 60;

    if (hours === 0) {
      return `${minutes} min`;
    }

    if (minutes === 0) {
      return `${hours} h`;
    }

    return `${hours} h ${minutes
      .toString()
      .padStart(2, "0")}`;
  }

  return (
    <section className="results-section">
      <div className="results-header">
        <h2>
          {trips.length} trajet
          {trips.length > 1 ? "s" : ""} trouvé
          {trips.length > 1 ? "s" : ""}
        </h2>
      </div>

      {trips.length === 0 && (
        <p>Aucun trajet disponible.</p>
      )}

      <div className="trip-list">
        {trips.map((trip) => (
          <article
            key={trip.trip_id}
            className="trip-card"
          >
            <div className="trip-card-top">
              <span className="train-number">
                Train {trip.train_number}
              </span>

              <span className="trip-status">
                Prévu
              </span>
            </div>

            <div className="trip-card-main">
              <div className="trip-point">
                <strong>
                  {formatTime(
                    trip.departure_datetime
                  )}
                </strong>

                <span>
                  {trip.departure}
                </span>
              </div>

              <div className="trip-duration">
                <span>
                  {getDuration(
                    trip.departure_datetime,
                    trip.arrival_datetime
                  )}
                </span>

                <div className="trip-line">
                  <span />
                </div>
              </div>

              <div className="trip-point trip-point-arrival">
                <strong>
                  {formatTime(
                    trip.arrival_datetime
                  )}
                </strong>

                <span>
                  {trip.arrival}
                </span>
              </div>
            </div>

            <div className="trip-card-footer">
              <button
                type="button"
                onClick={() =>
                  onTripDetail(trip.trip_id)
                }
              >
                Voir le détail
              </button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

export default TripList;