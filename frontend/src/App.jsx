import { useEffect, useState } from "react";

import SearchForm from "./components/SearchForm";
import TripList from "./components/TripList";
import TripDetail from "./components/TripDetail";

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

  const [selectedTrip, setSelectedTrip] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

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
      setError(
        "Sélectionne une gare de départ et une gare d'arrivée."
      );
      return;
    }

    setLoading(true);
    setError(null);
    setSearched(true);
    setSelectedTrip(null);

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

  async function handleTripDetail(tripId) {
    setDetailLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/trips/${tripId}`
      );

      if (!response.ok) {
        throw new Error(
          "Impossible de récupérer le détail du trajet."
        );
      }

      const data = await response.json();

      setSelectedTrip(data);
    } catch (error) {
      setError(error.message);
    } finally {
      setDetailLoading(false);
    }
  }

  return (
    <main>
      <h1>Smart Mobility</h1>

      <h2>Trouvez votre trajet</h2>

      <SearchForm
        stations={stations}
        departure={departure}
        setDeparture={setDeparture}
        arrival={arrival}
        setArrival={setArrival}
        travelDate={travelDate}
        setTravelDate={setTravelDate}
        departureAfter={departureAfter}
        setDepartureAfter={setDepartureAfter}
        onSearch={handleSearch}
      />

      {error && <p>{error}</p>}

      <TripList
        trips={trips}
        searched={searched}
        loading={loading}
        onTripDetail={handleTripDetail}
      />

      <TripDetail
        trip={selectedTrip}
        loading={detailLoading}
        onClose={() => setSelectedTrip(null)}
      />
    </main>
  );
}

export default App;