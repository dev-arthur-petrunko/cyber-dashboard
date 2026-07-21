"use client";

/**
 * Сигнатурний елемент дашборда: тонка ЕКГ-лінія вгорі сторінки,
 * що візуалізує обсяг нових загроз за годинами протягом останніх 24 годин.
 */
export function PulseStrip({ hourlyVolume }: { hourlyVolume: number[] }) {
  const width = 1200;
  const height = 40;
  const max = Math.max(...hourlyVolume, 1);

  const points = hourlyVolume
    .map((v, i) => {
      const x = (i / (hourlyVolume.length - 1)) * width;
      const y = height - (v / max) * (height - 6) - 3;
      return `${x},${y}`;
    })
    .join(" ");

  // Area fill path
  const areaPath = `M0,${height} L${points.split(" ").map((p, i) => (i === 0 ? `0,${height} L${p}` : p)).join(" L")} L${width},${height} Z`;

  return (
    <div className="relative w-full overflow-hidden border-b border-border/50 bg-gradient-to-r from-panel via-panel-raised to-panel">
      {/* Subtle grid overlay */}
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)",
          backgroundSize: "20px 10px",
        }}
      />

      <svg
        viewBox={`0 0 ${width} ${height}`}
        preserveAspectRatio="none"
        className="relative h-10 w-full"
        role="img"
        aria-label="Threat activity over last 24 hours"
      >
        <defs>
          <linearGradient id="pulse-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#10B981" stopOpacity="0.3" />
            <stop offset="50%" stopColor="#10B981" stopOpacity="1" />
            <stop offset="100%" stopColor="#3B82F6" stopOpacity="0.8" />
          </linearGradient>
          <linearGradient id="pulse-area-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#10B981" stopOpacity="0.15" />
            <stop offset="100%" stopColor="#10B981" stopOpacity="0" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Area fill under the line */}
        <path d={areaPath} fill="url(#pulse-area-gradient)" />

        {/* Main pulse line with glow */}
        <polyline
          points={points}
          fill="none"
          stroke="url(#pulse-gradient)"
          strokeWidth="2"
          strokeLinejoin="round"
          strokeLinecap="round"
          filter="url(#glow)"
        />

        {/* Animated scanning dot */}
        <circle r="3" fill="#10B981">
          <animateMotion dur="8s" repeatCount="indefinite" path={`M0,0 L${points}`} />
          <animate attributeName="opacity" values="1;0.5;1" dur="1.5s" repeatCount="indefinite" />
        </circle>

        {/* Pulsing endpoint */}
        <circle
          cx={width}
          cy={height - (hourlyVolume[hourlyVolume.length - 1] / max) * (height - 6) - 3}
          r="3"
          fill="#10B981"
        >
          <animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite" />
          <animate attributeName="r" values="3;5;3" dur="2s" repeatCount="indefinite" />
        </circle>

        {/* Glow ring around endpoint */}
        <circle
          cx={width}
          cy={height - (hourlyVolume[hourlyVolume.length - 1] / max) * (height - 6) - 3}
          r="6"
          fill="none"
          stroke="#10B981"
          strokeWidth="1"
        >
          <animate attributeName="opacity" values="0.5;0;0.5" dur="2s" repeatCount="indefinite" />
          <animate attributeName="r" values="6;12;6" dur="2s" repeatCount="indefinite" />
        </circle>
      </svg>
    </div>
  );
}
