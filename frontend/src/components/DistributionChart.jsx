import { Pie } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

export default function DistributionChart({ data }) {
  const chartData = {
    labels: ["Positive", "Negative", "Neutral"],
    datasets: [
      {
        data: [
          data.Positive || 0,
          data.Negative || 0,
          data.Neutral || 0,
        ],
        backgroundColor: ["#22c55e", "#ef4444", "#94a3b8"],
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
  };

  return (
    <div style={{ height: "100%", width: "100%", display: "flex", flexDirection: "column" }}>
      <h3 style={{ margin: "0 0 10px 0" }}>Sentiment Distribution</h3>
      <div style={{ flex: 1, minHeight: "280px" }}>
        <Pie data={chartData} options={options} />
      </div>
    </div>
  );
}