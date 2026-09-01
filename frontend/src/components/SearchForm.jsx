import { useEffect, useState } from "react";

function SearchForm({
  departure,
  setDeparture,
  arrival,
  setArrival,

  departureName,
  setDepartureName,

  arrivalName,
  setArrivalName,

  travelDate,
  setTravelDate,
  departureAfter,
  setDepartureAfter,
  onSearch,
  onSwapStations,
}) {
  const [departureQuery, setDepartureQuery] = useState("");
  const [arrivalQuery, setArrivalQuery] = useState("");

  const [departureSuggestions, setDepartureSuggestions] =
    useState([]);
  const [arrivalSuggestions, setArrivalSuggestions] =
    useState([]);

  async function searchStations(query, setSuggestions) {
    if (query.length < 2) {
      setSuggestions([]);
      return;
    }

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/stations/search?q=${encodeURIComponent(
          query
        )}`
      );

      if (!response.ok) {
        throw new Error(
          "Erreur lors de la recherche des gares."
        );
      }

      const data = await response.json();
      setSuggestions(data);
    } catch (error) {
      console.error(error);
      setSuggestions([]);
    }
  }

  /* =========================
     SYNCHRONISATION AVEC APP
     ========================= */

  useEffect(() => {
    setDepartureQuery(departureName || "");
  }, [departureName]);

  useEffect(() => {
    setArrivalQuery(arrivalName || "");
  }, [arrivalName]);

  /* =========================
     AUTOCOMPLÉTION DÉPART
     ========================= */

  useEffect(() => {
    if (departure) {
      setDepartureSuggestions([]);
      return;
    }

    const timer = setTimeout(() => {
      searchStations(
        departureQuery,
        setDepartureSuggestions
      );
    }, 300);

    return () => clearTimeout(timer);
  }, [departureQuery, departure]);

  /* =========================
     AUTOCOMPLÉTION ARRIVÉE
     ========================= */

  useEffect(() => {
    if (arrival) {
      setArrivalSuggestions([]);
      return;
    }

    const timer = setTimeout(() => {
      searchStations(
        arrivalQuery,
        setArrivalSuggestions
      );
    }, 300);

    return () => clearTimeout(timer);
  }, [arrivalQuery, arrival]);

  function handleDepartureChange(event) {
  const value = event.target.value;

  setDepartureQuery(value);

  setDeparture("");
  setDepartureName("");
}

function handleArrivalChange(event) {
  const value = event.target.value;

  setArrivalQuery(value);

  setArrival("");
  setArrivalName("");
}  
 function selectDeparture(station) {
  setDepartureQuery(station.name);

  setDeparture(station.external_id);
  setDepartureName(station.name);

  setDepartureSuggestions([]);
}
 function selectArrival(station) {
  setArrivalQuery(station.name);

  setArrival(station.external_id);
  setArrivalName(station.name);

  setArrivalSuggestions([]);
} 

  return (
    <form onSubmit={onSearch}>
      {/* DÉPART */}
      <div>
        <label>Départ</label>

        <input
          type="text"
          value={departureQuery}
          onChange={handleDepartureChange}
          placeholder="Ex : Paris"
          autoComplete="off"
        />

        {departureSuggestions.length > 0 && (
          <ul>
            {departureSuggestions.map((station) => (
              <li key={station.id}>
                <button
                  type="button"
                  onClick={() =>
                    selectDeparture(station)
                  }
                >
                  {station.name}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* INVERSER */}
      <div className="swap-container">
        <button
          type="button"
          className="swap-button"
          onClick={onSwapStations}
          aria-label="Inverser le départ et l'arrivée"
          title="Inverser départ et arrivée"
        >
          ⇄
        </button>
      </div>

      {/* ARRIVÉE */}
      <div>
        <label>Arrivée</label>

        <input
          type="text"
          value={arrivalQuery}
          onChange={handleArrivalChange}
          placeholder="Ex : Lyon"
          autoComplete="off"
        />

        {arrivalSuggestions.length > 0 && (
          <ul>
            {arrivalSuggestions.map((station) => (
              <li key={station.id}>
                <button
                  type="button"
                  onClick={() =>
                    selectArrival(station)
                  }
                >
                  {station.name}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* DATE */}
      <div>
        <label>Date</label>

        <input
          type="date"
          value={travelDate}
          onChange={(event) =>
            setTravelDate(event.target.value)
          }
        />
      </div>

      {/* HEURE */}
      <div>
        <label>Après</label>

        <input
          type="time"
          value={departureAfter}
          onChange={(event) =>
            setDepartureAfter(event.target.value)
          }
        />
      </div>

      <button type="submit">
        Rechercher
      </button>
    </form>
  );
}

export default SearchForm;