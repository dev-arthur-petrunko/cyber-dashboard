"use client";

import { Region } from "@/lib/types";
import { UaFlag } from "./UaFlag";
import { useTranslation } from "./LanguageContext";

export function RegionToggle({
  value,
  onChange,
}: {
  value: Region | undefined;
  onChange: (region: Region | undefined) => void;
}) {
  const { t } = useTranslation();
  const options: { label: string; value: Region | undefined; icon?: React.ReactNode }[] = [
    { label: t.region.all, value: undefined },
    { label: t.region.ukraine, value: "UA", icon: <UaFlag className="h-3.5 w-5 rounded-sm shadow-sm" /> },
    { label: t.region.world, value: "World", icon: <GlobeIcon /> },
  ];

  return (
    <div className="inline-flex rounded-lg border border-border bg-panel p-0.5 shadow-sm sm:rounded-xl sm:p-1">
      {options.map((opt) => {
        const active = opt.value === value;
        return (
          <button
            key={opt.label}
            onClick={() => onChange(opt.value)}
            className={`relative flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium transition-all sm:gap-2 sm:rounded-lg sm:px-4 sm:py-2 sm:text-sm ${
              active
                ? "bg-gradient-to-r from-signal/20 to-info/20 text-text-primary shadow-sm"
                : "text-text-secondary hover:text-text-primary hover:bg-panel-raised"
            }`}
          >
            {opt.icon}
            <span className="hidden sm:inline">{opt.label}</span>
            {opt.icon && <span className="sm:hidden">{opt.label.charAt(0)}</span>}
            {active && opt.value === "UA" && (
              <span className="absolute inset-x-2 -bottom-[2px] h-[2px] rounded-full bg-ua-gold sm:inset-x-3" />
            )}
          </button>
        );
      })}
    </div>
  );
}

function GlobeIcon() {
  return (
    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 013 12c0-1.605.42-3.113 1.157-4.418" />
    </svg>
  );
}
