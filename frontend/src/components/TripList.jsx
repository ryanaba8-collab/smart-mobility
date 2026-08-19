function TripList({ trips, searched, loading, onTripDetail }) {
  if (loading) {
    return <p>Recherche en cours...</p>;
  }

  if (!searched) {
    return null;
  }

  return (
    <section>
      <h2>
        {trips.length} trajet{trips.length > 1 ? "s" : ""} trouvé
        {trips.length > 1 ? "s" : ""}
      </h2>

      {trips.length === 0 && <p>Aucun trajet disponible.</p>}

      {trips.map((trip) => (
        <article key={trip.trip_id}>
          <h3>{trip.train_number}</h3>

          <p>
            {new Date(trip.departure_datetime).toLocaleTimeString(
              "fr-FR",
              { hour: "2-digit", minute: "2-digit" }
            )}
            {" → "}
            {new Date(trip.arrival_datetime).toLocaleTimeString(
              "fr-FR",
              { hour: "2-digit", minute: "2-digit" }
            )}
          </p>

          <p>
            {trip.departure} → {trip.arrival}
          </p>

          <strong>{trip.price.toFixed(2)} €</strong>

          <button
            type="button"
            onClick={() => onTripDetail(trip.trip_id)}
          >
            Voir le détail
          </button>
        </article>
      ))}
    </section>
  );
}

export default TripList;