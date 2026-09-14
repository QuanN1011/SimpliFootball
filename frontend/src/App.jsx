import { useEffect, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

export default function App() {
  const [summary, setSummary] = useState(null);
  const [topPlayers, setTopPlayers] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([
      fetch(`${API}/shots/summary`).then((r) => r.json()),
      fetch(`${API}/shots/top-players`).then((r) => r.json()),
    ])
      .then(([summaryData, playersData]) => {
        setSummary(summaryData);
        setTopPlayers(playersData);
      })
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <p>Error: {error}</p>;
  if (!summary) return <p>Loading…</p>;

  return (
    <main style={{ fontFamily: "system-ui", padding: "2rem", maxWidth: 800 }}>
      <h1>SimpliFootball</h1>
      <p>
        Shots: {summary.total_shots} · Players: {summary.players} · Matches:{" "}
        {summary.matches_with_shots}
      </p>

      <h2>Top players by shots</h2>
      <table cellPadding="8">
        <thead>
          <tr>
            <th align="left">Player</th>
            <th align="right">Shots</th>
            <th align="right">xG</th>
          </tr>
        </thead>
        <tbody>
          {topPlayers.map((p) => (
            <tr key={p.player_name}>
              <td>{p.player_name}</td>
              <td align="right">{p.shots}</td>
              <td align="right">{p.total_xg}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}