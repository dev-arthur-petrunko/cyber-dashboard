"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { fetchTimeline } from "@/lib/api";
import { Timeline } from "@/lib/types";
import { CyberTimeline } from "@/components/CyberTimeline";
import { ThemeToggle } from "@/components/ThemeToggle";
import { LanguageToggle } from "@/components/LanguageToggle";
import { useTranslation } from "@/components/LanguageContext";

export default function TimelinePage() {
  const params = useParams<{ cve: string }>();
  const router = useRouter();
  const { t } = useTranslation();
  const [timeline, setTimeline] = useState<Timeline | null>(null);
  const [isDemo, setIsDemo] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchTimeline(params.cve).then(({ data, isDemo }) => {
      setTimeline(data);
      setIsDemo(isDemo);
      setLoading(false);
    });
  }, [params.cve]);

  return (
    <main className="min-h-screen bg-bg">
      <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
        <div className="mb-6 flex items-center justify-between">
          <button
            onClick={() => router.push("/")}
            className="inline-flex items-center gap-2 rounded-lg border border-border bg-panel px-4 py-2 text-sm font-medium text-text-secondary hover:text-signal hover:border-signal/40 shadow-sm transition-all"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            {t.timeline.backToDashboard}
          </button>
          <div className="flex items-center gap-2">
            <LanguageToggle />
            <ThemeToggle />
          </div>
        </div>

        <div className="mb-6">
          <h1 className="font-mono text-2xl font-bold text-text-primary">{params.cve}</h1>
          <p className="mt-1 text-sm text-text-secondary">{t.timeline.title}</p>
        </div>

        {isDemo && !loading && (
          <div className="mb-6 rounded-xl border border-warning/30 bg-warning/10 px-4 py-3 text-sm text-warning shadow-sm">
            ⚠️ {t.timeline.demoWarning}
          </div>
        )}

        {loading ? (
          <div className="rounded-xl border border-border bg-panel p-8 text-center shadow-sm">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-signal border-t-transparent" />
            <p className="mt-3 text-sm text-text-muted">{t.timeline.loading}</p>
          </div>
        ) : (
          timeline && <CyberTimeline timeline={timeline} />
        )}
      </div>
    </main>
  );
}
