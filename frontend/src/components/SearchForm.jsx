function SearchForm({
  stations,
  departure,
  setDeparture,
  arrival,
  setArrival,
  travelDate,
  setTravelDate,
  departureAfter,
  setDepartureAfter,
  onSearch,
}) {
  return (
    <form onSubmit={onSearch}>
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

      <button type="submit">Rechercher</button>
    </form>
  );
}

export default SearchForm;