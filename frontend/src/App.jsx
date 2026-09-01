import { useEffect, useState } from "react";
import "./App.css";
import SearchForm from "./components/SearchForm";
import TripList from "./components/TripList";
import TripDetail from "./components/TripDetail";

function App() {
  const [departure, setDeparture] = useState("");
  const [arrival, setArrival] = useState("");
  const [travelDate, setTravelDate] = useState("2026-08-25");
  const [departureAfter, setDepartureAfter] = useState("18:00");

  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState(null);

  const [selectedTrip, setSelectedTrip] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [departureName, setDepartureName] = useState("");
  const [arrivalName, setArrivalName] = useState("");

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
      const errorData = await response.json();

      throw new Error(
      errorData.detail || "La recherche a échoué."
  );
}
      const data = await response.json();
      

      setTrips(data);
      await loadHistory();
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
  async function loadHistory() {
  try {
    const response = await fetch(
      "http://127.0.0.1:8000/searches/history?limit=5"
    );

    if (!response.ok) {
      throw new Error("Impossible de récupérer l'historique.");
    }

    const data = await response.json();
    setHistory(data);
  } catch (error) {
    console.error(error);
  }
}
function handleHistoryClick(search) {
  setDeparture(search.departure_external_id);
  setArrival(search.arrival_external_id);

  setDepartureName(search.departure);
  setArrivalName(search.arrival);

  setTravelDate(search.travel_date);
  setDepartureAfter(search.departure_after.slice(0, 5));

  setTrips([]);
  setSearched(false);
  setSelectedTrip(null);
  setError(null);
}
function handleSwapStations() {
  const oldDeparture = departure;
  const oldDepartureName = departureName;

  setDeparture(arrival);
  setArrival(oldDeparture);

  setDepartureName(arrivalName);
  setArrivalName(oldDepartureName);

  setTrips([]);
  setSearched(false);
  setSelectedTrip(null);
  setError(null);
}
useEffect(() => {
  loadHistory();
}, []);

  return (
    <main>
      <h1>Smart Mobility</h1>

      <h2>Trouvez votre trajet</h2>

      <SearchForm
        departure={departure}
        setDeparture={setDeparture}
        arrival={arrival}
        setArrival={setArrival}

        departureName={departureName}
        setDepartureName={setDepartureName}

        arrivalName={arrivalName}
        setArrivalName={setArrivalName}

        travelDate={travelDate}
        setTravelDate={setTravelDate}

        departureAfter={departureAfter}
        setDepartureAfter={setDepartureAfter}

        onSearch={handleSearch}
        onSwapStations={handleSwapStations}
     />
      {history.length > 0 && (
  <section className="history-section">
  <h3>Recherches récentes</h3>

  <ul className="history-list">
      {history.map((search) => (
    <li key={search.id}>
    <button
      type="button"
      onClick={() => handleHistoryClick(search)}
    >
      <strong>
        {search.departure} → {search.arrival}
      </strong>

          <div>
            {search.travel_date} après{" "}
            {search.departure_after.slice(0, 5)}
          </div>
        </button>
      </li>
     ))}
    </ul>
  </section>
)}

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