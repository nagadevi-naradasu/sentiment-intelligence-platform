import React, { useEffect, useState } from "react";
import { fetchAlerts, fetchSentimentDistribution } from "../services/api";
import DistributionChart from "./DistributionChart";
import SentimentChart from "./SentimentChart";

export default function Dashboard() {
  const [alerts, setAlerts] = useState([]);
  const [distribution, setDistribution] = useState({ Positive: 0, Negative: 0, Neutral: 0 });
  const [livePosts, setLivePosts] = useState([]);
  const [trend, setTrend] = useState([]);

  useEffect(() => {
    fetchAlerts().then(setAlerts);
    fetchSentimentDistribution().then(data => {
      if (data) {
        // Normalize keys from API (lower) to State (Upper)
        const normalized = {
          Positive: data.positive || data.Positive || 0,
          Negative: data.negative || data.Negative || 0,
          Neutral: data.neutral || data.Neutral || 0
        };
        setDistribution(normalized);
      }
    });
  }, []);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/live");

    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);

      if (data.type === "sentiment") {
        // Fix case sensitivity: "positive" -> "Positive"
        const s = data.sentiment;
        const normalizedS = s.charAt(0).toUpperCase() + s.slice(1).toLowerCase();

        setLivePosts((prev) => [{...data, sentiment: normalizedS}, ...prev].slice(0, 10));

        setDistribution((prev) => ({
          ...prev,
          [normalizedS]: (prev[normalizedS] || 0) + 1,
        }));

        setTrend((prev) => [...prev.slice(-23), {...data, sentiment: normalizedS}]);
      }

      if (data.type === "alert") {
        setAlerts((prev) => [data, ...prev].slice(0, 10));
      }
    };

    return () => ws.close();
  }, []);

  const total = (distribution.Positive || 0) + (distribution.Negative || 0) + (distribution.Neutral || 0);

  return (
    <div style={{ padding: 20, fontFamily: "Arial", backgroundColor: "#f8fafc", minHeight: "100vh" }}>
      <h1>📊 Sentiment Intelligence Dashboard</h1>

      <div style={{ display: "flex", gap: 20 }}>
        {/* Added fixed width/height for Chart visibility */}
        <div style={{ ...card, width: "400px", height: "400px" }}>
          <DistributionChart data={distribution} />
        </div>

        <div style={{ ...card, flex: 1, height: "400px" }}>
          <h3>Recent Posts Feed</h3>
          <div style={liveFeed}>
            {livePosts.length === 0 && <p style={{ color: "#999" }}>Waiting for live data…</p>}
            {livePosts.map((p, i) => (
              <div key={i} style={feedItem}>
                <b style={{ color: p.sentiment === 'Positive' ? 'green' : p.sentiment === 'Negative' ? 'red' : 'gray' }}>
                  {p.sentiment}
                </b> — {p.emotion || 'Analyzing...'}
                <p style={{ margin: "4px 0 0 0", fontSize: "12px", color: "#666" }}>{p.content}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div style={{ ...card, marginTop: 20, height: "350px" }}>
        <SentimentChart feed={trend} />
      </div>

      <div style={{ display: "flex", gap: 20, marginTop: 20 }}>
        <Stat title="Total" value={total} />
        <Stat title="Positive" value={distribution.Positive} />
        <Stat title="Negative" value={distribution.Negative} />
        <Stat title="Neutral" value={distribution.Neutral} />
      </div>
    </div>
  );
}

const card = { background: "#fff", borderRadius: 8, padding: 16, boxShadow: "0 2px 8px rgba(0,0,0,0.08)" };
const liveFeed = { maxHeight: "320px", overflowY: "auto" };
const feedItem = { padding: 10, background: "#f9f9f9", borderRadius: 4, marginBottom: 8, borderLeft: "4px solid #ddd" };

function Stat({ title, value }) {
  return (
    <div style={{ ...card, flex: 1, textAlign: "center" }}>
      <h4 style={{ margin: 0, color: "#64748b" }}>{title}</h4>
      <h2 style={{ margin: "10px 0 0 0" }}>{value || 0}</h2>
    </div>
  );
}