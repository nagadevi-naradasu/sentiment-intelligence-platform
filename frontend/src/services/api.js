import axios from "axios";

const API_BASE = "http://localhost:8000";

export const fetchAlerts = async () => {
  const res = await axios.get(`${API_BASE}/api/alerts`);
  return res.data;
};

export const fetchSentimentDistribution = async () => {
  const res = await axios.get(`${API_BASE}/api/sentiment/distribution`);
  return res.data;
};
