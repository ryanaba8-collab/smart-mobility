function TripDetail({ trip, loading, onClose }) {
  if (loading) {
    return <p>Chargement du trajet...</p>;
  }

  if (!trip) {
    return null;
  }

  return (
    <section>
      <h2>Détail du trajet</h2>

      <h3>{trip.train_number}</h3>

      <p>
        <strong>Départ :</strong> {trip.departure_station}
      </p>

      <p>
        {new Date(trip.departure_datetime).toLocaleString("fr-FR")}
      </p>

      <p>↓</p>

      <p>
        <strong>Arrivée :</strong> {trip.arrival_station}
      </p>

      <p>
        {new Date(trip.arrival_datetime).toLocaleString("fr-FR")}
      </p>

      <p>
        <strong>Durée :</strong>{" "}
        {Math.floor(trip.duration_minutes / 60)} h{" "}
        {trip.duration_minutes % 60} min
      </p>

      <p>
        <strong>Distance :</strong> {trip.distance_km} km
      </p>

      <p>
        <strong>Prix :</strong> {trip.price.toFixed(2)} €
      </p>

      <p>
        <strong>Statut :</strong> {trip.status}
      </p>

      <button type="button" onClick={onClose}>
        Fermer
      </button>
    </section>
  );
}

export default TripDetail;