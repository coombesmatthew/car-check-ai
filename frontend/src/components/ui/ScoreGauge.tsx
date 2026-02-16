interface ScoreGaugeProps {
  score: number;
  size?: number;
  label?: string;
}

export default function ScoreGauge({
  score,
  size = 120,
  label = "Condition Score",
}: ScoreGaugeProps) {
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const clampedScore = Math.max(0, Math.min(100, score));
  const offset = circumference - (clampedScore / 100) * circumference;

  const color =
    clampedScore >= 80
      ? "#059669"
      : clampedScore >= 50
      ? "#f59e0b"
      : "#dc2626";

  const bgColor =
    clampedScore >= 80
      ? "#d1fae5"
      : clampedScore >= 50
      ? "#fef3c7"
      : "#fee2e2";

  return (
    <div className="flex flex-col items-center">
      <svg
        width={size}
        height={size}
        viewBox="0 0 100 100"
        className="transform -rotate-90"
      >
        <circle
          cx="50"
          cy="50"
          r={radius}
          fill="none"
          stroke="#e2e8f0"
          strokeWidth="8"
          strokeLinecap="round"
        />
        <circle
          cx="50"
          cy="50"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div
        className="flex flex-col items-center -mt-[76px] mb-4"
        style={{ marginTop: -(size * 0.63) , marginBottom: size * 0.03 }}
      >
        <span
          className="font-bold"
          style={{ fontSize: size * 0.28, color }}
        >
          {clampedScore}
        </span>
        <span
          className="font-medium rounded-full px-2 py-0.5"
          style={{ fontSize: size * 0.09, color, backgroundColor: bgColor }}
        >
          {clampedScore >= 80 ? "Good" : clampedScore >= 50 ? "Fair" : "Poor"}
        </span>
      </div>
      <p className="text-xs text-slate-400 mt-1">{label}</p>
    </div>
  );
}
