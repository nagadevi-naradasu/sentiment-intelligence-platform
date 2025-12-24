import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend,
  Filler
} from "chart.js";

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Legend, Filler);

export default function SentimentChart({ feed }) {
  // 1. Calculate the running total (Cumulative Sum)
  let posCount = 0;
  let negCount = 0;

  const positiveTrend = feed.map((item) => {
    if (item.sentiment === "Positive") posCount++;
    return posCount;
  });

  const negativeTrend = feed.map((item) => {
    if (item.sentiment === "Negative") negCount++;
    return negCount;
  });

  const data = {
    labels: feed.map((_, i) => i + 1),
    datasets: [
      {
        label: "Positive Growth",
        data: positiveTrend,
        borderColor: "#22c55e",
        backgroundColor: "rgba(34, 197, 94, 0.1)",
        tension: 0.4,
        fill: true,
        pointRadius: 2,
      },
      {
        label: "Negative Growth",
        data: negativeTrend,
        borderColor: "#ef4444",
        backgroundColor: "rgba(239, 68, 68, 0.1)",
        tension: 0.4,
        fill: true,
        pointRadius: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          precision: 0, // Ensure we only show whole numbers (1, 2, 3...)
        },
        grid: { color: "#f1f5f9" }
      },
      x: {
        grid: { display: false }
      }
    },
    plugins: {
      legend: { position: 'top' },
      tooltip: { mode: 'index', intersect: false } // Shows both values when hovering
    }
  };

  return (
    <div style={{ height: "100%", width: "100%" }}>
      <h3 style={{ margin: "0 0 10px 0", fontSize: "16px", color: "#1e293b" }}>
        Cumulative Sentiment Growth
      </h3>
      <div style={{ height: "250px" }}>
        <Line data={data} options={options} />
      </div>
    </div>
  );
}