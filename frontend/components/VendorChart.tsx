"use client";

import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell } from "recharts";

export function VendorChart({ data }: { data: { vendor: string; count: number }[] }) {
  const [animated, setAnimated] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setAnimated(true), 300);
    return () => clearTimeout(timer);
  }, []);

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center py-8">
        <p className="text-sm text-text-muted">No vendor data yet</p>
      </div>
    );
  }

  const colors = [
    "#EF4444", // critical red
    "#10B981", // signal green
    "#3B82F6", // info blue
    "#F59E0B", // warning amber
    "#8B5CF6", // purple
  ];

  return (
    <div className="relative">
      {/* Subtle background glow */}
      <div className="pointer-events-none absolute inset-0 rounded-xl bg-gradient-to-br from-signal/5 via-transparent to-info/5 opacity-50" />

      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} layout="vertical" margin={{ left: 8, right: 16, top: 4, bottom: 4 }}>
          <defs>
            {colors.map((color, i) => (
              <linearGradient key={i} id={`bar-gradient-${i}`} x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor={color} stopOpacity={0.9} />
                <stop offset="100%" stopColor={color} stopOpacity={0.6} />
              </linearGradient>
            ))}
          </defs>
          <XAxis type="number" hide />
          <YAxis
            type="category"
            dataKey="vendor"
            width={90}
            tick={{ fontSize: 11, fill: "var(--text-secondary)" }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            contentStyle={{
              background: "var(--panel-raised)",
              border: "1px solid var(--border)",
              borderRadius: 10,
              boxShadow: "0 8px 32px -8px rgb(0 0 0 / 0.2)",
              backdropFilter: "blur(8px)",
              padding: "10px 14px",
            }}
            labelStyle={{ color: "var(--text-primary)", fontWeight: 700, fontSize: 13 }}
            itemStyle={{ color: "#10B981", fontWeight: 600 }}
            cursor={{ fill: "var(--panel-raised)", opacity: 0.5 }}
          />
          <Bar
            dataKey="count"
            radius={[0, 6, 6, 0]}
            animationDuration={1200}
            animationEasing="ease-out"
            isAnimationActive={animated}
          >
            {data.map((_, i) => (
              <Cell
                key={i}
                fill={`url(#bar-gradient-${i % colors.length})`}
                fillOpacity={0.85}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
