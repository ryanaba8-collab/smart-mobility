import { useEffect, useState } from "react";

function App() {
  const [stations, setStations] = useState([]);

  const [departure, setDeparture] = useState("");
  const [arrival, setArrival] = useState("");
  const [travelDate, setTravelDate] = useState("2026-08-20");
  const [departureAfter, setDepartureAfter] = useState("18:00");

  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/stations")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Impossible de récupérer les gares.");
        }

        return response.json();
      })
      .then((data) => {
        setStations(data);
      })
      .catch((error) => {
        setError(error.message);
      });
  }, []);

  async function handleSearch(event) {
    event.preventDefault();

    if (!departure || !arrival) {
      setError("Sélectionne une gare de départ et une gare d'arrivée.");
      return;
    }

    setLoading(true);
    setError(null);
    setSearched(true);

    const params = new URLSearchParams({
      departure,
      arrival,
      travel_date: travelDate,
      departure_after: departureAfter,
    });

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/trips/search?${params}`
      );

      if (!response.ok) {
        throw new Error("La recherche a échoué.");
      }

      const data = await response.json();

      setTrips(data);
    } catch (error) {
      setError(error.message);
      setTrips([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <h1>Smart Mobility</h1>

      <h2>Trouvez votre trajet</h2>

      <form onSubmit={handleSearch}>
        <div>
          <label>Départ</label>

          <select
            value={departure}
            onChange={(event) => setDeparture(event.target.value)}
          >
            <option value="">Choisir une gare</option>

            {stations.map((station) => (
              <option key={station.id} value={station.name}>
                {station.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label>Arrivée</label>

          <select
            value={arrival}
            onChange={(event) => setArrival(event.target.value)}
          >
            <option value="">Choisir une gare</option>

            {stations.map((station) => (
              <option key={station.id} value={station.name}>
                {station.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label>Date</label>

          <input
            type="date"
            value={travelDate}
            onChange={(event) => setTravelDate(event.target.value)}
          />
        </div>

        <div>
          <label>Après</label>

          <input
            type="time"
            value={departureAfter}
            onChange={(event) => setDepartureAfter(event.target.value)}
          />
        </div>

        <button type="submit">
          Rechercher
        </button>
      </form>

      {loading && <p>Recherche en cours...</p>}

      {error && <p>{error}</p>}

      {!loading && searched && !error && (
        <section>
          <h2>
            {trips.length} trajet{trips.length > 1 ? "s" : ""} trouvé
            {trips.length > 1 ? "s" : ""}
          </h2>

          {trips.length === 0 && (
            <p>Aucun trajet disponible.</p>
          )}

          {trips.map((trip) => (
            <article key={trip.trip_id}>
              <h3>{trip.train_number}</h3>

              <p>
                {new Date(trip.departure_datetime).toLocaleTimeString(
                  "fr-FR",
                  {
                    hour: "2-digit",
                    minute: "2-digit",
                  }
                )}
                {" → "}
                {new Date(trip.arrival_datetime).toLocaleTimeString(
                  "fr-FR",
                  {
                    hour: "2-digit",
                    minute: "2-digit",
                  }
                )}
              </p>

              <p>
                {trip.departure} → {trip.arrival}
              </p>

              <strong>{trip.price.toFixed(2)} €</strong>
            </article>
          ))}
        </section>
      )}
    </main>
  );
}

export default App;