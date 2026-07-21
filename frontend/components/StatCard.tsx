import { ReactNode, useEffect, useState, useRef } from "react";

export function StatCard({
  label,
  value,
  accent,
  icon,
  delay = 0,
}: {
  label: string;
  value: number | string;
  accent?: "critical" | "warning" | "signal" | "default";
  icon?: ReactNode;
  delay?: number;
}) {
  const accentColor = {
    critical: "text-critical",
    warning: "text-warning",
    signal: "text-signal",
    default: "text-text-primary",
  }[accent ?? "default"];

  const barColor = {
    critical: "bg-critical",
    warning: "bg-warning",
    signal: "bg-signal",
    default: "bg-border",
  }[accent ?? "default"];

  const glowColor = {
    critical: "hover:shadow-critical/30",
    warning: "hover:shadow-warning/30",
    signal: "hover:shadow-signal/30",
    default: "",
  }[accent ?? "default"];

  const iconBg = {
    critical: "bg-critical/10 group-hover:bg-critical/20",
    warning: "bg-warning/10 group-hover:bg-warning/20",
    signal: "bg-signal/10 group-hover:bg-signal/20",
    default: "bg-panel-raised group-hover:bg-panel-raised/80",
  }[accent ?? "default"];

  // Count-up animation for numeric values
  const [displayValue, setDisplayValue] = useState(typeof value === "number" ? 0 : value);
  const prevValue = useRef(value);

  useEffect(() => {
    if (typeof value !== "number") {
      setDisplayValue(value);
      return;
    }
    const target = value;
    const duration = 1500;
    const startTime = performance.now();

    function animate(now: number) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 4); // ease-out quart for smoother feel
      setDisplayValue(Math.round(eased * target));
      if (progress < 1) requestAnimationFrame(animate);
    }
    requestAnimationFrame(animate);
    prevValue.current = value;
  }, [value]);

  return (
    <div
      className={`animate-slide-up-fade group glass-card relative overflow-hidden rounded-xl border border-border p-4 shadow-sm transition-all duration-500 hover:shadow-xl hover:-translate-y-1 hover:border-signal/30 ${glowColor}`}
      style={{ animationDelay: `${delay}ms` }}
    >
      {/* Animated scan line on hover */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden opacity-0 transition-opacity duration-300 group-hover:opacity-100">
        <div className="animate-scan-line absolute inset-y-0 w-1/3 bg-gradient-to-r from-transparent via-white/5 to-transparent" />
      </div>

      <div className="relative flex items-start justify-between">
        <div className="flex-1">
          <p className="text-xs font-semibold uppercase tracking-wider text-text-secondary transition-colors group-hover:text-text-primary/70">{label}</p>
          <p className={`mt-2 font-mono text-3xl font-black leading-none ${accentColor} transition-all duration-500 group-hover:scale-105 origin-left`}>
            {displayValue}
          </p>
        </div>
        {icon && (
          <span className={`${iconBg} flex h-10 w-10 items-center justify-center rounded-lg transition-all duration-500 group-hover:scale-110 group-hover:rotate-3`}>
            {icon}
          </span>
        )}
      </div>

      {/* Bottom accent bar with gradient animation */}
      <div className={`absolute inset-x-0 bottom-0 h-1 ${barColor} transition-all duration-500 group-hover:h-1.5`}>
        <div className="animate-gradient-shift h-full w-full bg-gradient-to-r from-transparent via-white/20 to-transparent bg-[length:200%_100%]" />
      </div>
    </div>
  );
}
