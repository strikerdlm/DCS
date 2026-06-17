import React, { useEffect, useState } from "react";
import {
  BarChart3,
  Beaker,
  Brain,
  ClipboardCheck,
  Github,
  Home,
  Layers,
  ListOrdered,
  Mountain,
  Moon,
  Plane,
  Rocket,
  Sun,
  Wind,
} from "lucide-react";
import { EVASimulator } from "./components/eva";
import {
  Anatomy,
  MLSurrogate,
  Mechanistic3RUT,
  NASALogistic,
  Overview,
  StepByStep,
  UseCases,
  ValidationDashboard,
} from "./components/models";
import { cn } from "./lib/utils";

type ModelTab =
  | "overview"
  | "anatomy"
  | "steps"
  | "usecases"
  | "eva"
  | "ml"
  | "mechanistic"
  | "nasa"
  | "validation";

interface NavItem {
  id: ModelTab;
  label: string;
  description: string;
  icon: React.ReactNode;
}

interface NavGroup {
  heading: string;
  items: NavItem[];
}

const NAV_GROUPS: NavGroup[] = [
  {
    heading: "Understand",
    items: [
      {
        id: "overview",
        label: "Overview",
        description: "How TinyDCS works · 3-layer stack",
        icon: <Home className="h-4 w-4" />,
      },
      {
        id: "anatomy",
        label: "Anatomy",
        description: "Physics · math · map · visual explainer",
        icon: <Layers className="h-4 w-4" />,
      },
      {
        id: "steps",
        label: "Step-by-step",
        description: "Inference pipeline, end to end",
        icon: <ListOrdered className="h-4 w-4" />,
      },
      {
        id: "usecases",
        label: "Use cases",
        description: "Two worked, live examples",
        icon: <Plane className="h-4 w-4" />,
      },
    ],
  },
  {
    heading: "Mission Planning",
    items: [
      {
        id: "eva",
        label: "EVA Simulator",
        description: "Habitat, suit, prebreathe, 5x5 risk",
        icon: <ClipboardCheck className="h-4 w-4" />,
      },
    ],
  },
  {
    heading: "Model Families",
    items: [
      {
        id: "ml",
        label: "ADRAC Risk Predictor",
        description: "Pilmanis 2004 log-logistic AFT",
        icon: <Brain className="h-4 w-4" />,
      },
      {
        id: "mechanistic",
        label: "3RUT‑MBe1",
        description: "Schematic preview · NEDU TR 18-01",
        icon: <Beaker className="h-4 w-4" />,
      },
      {
        id: "nasa",
        label: "NASA Conkin ETR",
        description: "Logistic · Eq. 14 / 15",
        icon: <Rocket className="h-4 w-4" />,
      },
      {
        id: "validation",
        label: "Validation",
        description: "Closed-form vs ADRAC grid",
        icon: <BarChart3 className="h-4 w-4" />,
      },
    ],
  },
];

const NAV_ITEMS: NavItem[] = NAV_GROUPS.flatMap((g) => g.items);

export default function App(): React.ReactElement {
  const [activeTab, setActiveTab] = useState<ModelTab>("overview");
  const [isDark, setIsDark] = useState(() =>
    typeof window === "undefined"
      ? true
      : !window.matchMedia?.("(prefers-color-scheme: light)").matches,
  );

  useEffect(() => {
    document.documentElement.classList.toggle("dark", isDark);
  }, [isDark]);

  const renderContent = () => {
    switch (activeTab) {
      case "overview":
        return <Overview />;
      case "anatomy":
        return <Anatomy />;
      case "steps":
        return <StepByStep />;
      case "usecases":
        return <UseCases />;
      case "eva":
        return <EVASimulator />;
      case "ml":
        return <MLSurrogate />;
      case "mechanistic":
        return <Mechanistic3RUT />;
      case "nasa":
        return <NASALogistic />;
      case "validation":
        return <ValidationDashboard />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top brand bar */}
      <header className="sticky top-0 z-40 border-b border-border/60 backdrop-blur-xl bg-background/70">
        <div className="max-w-[1480px] mx-auto px-6 lg:px-8 h-16 flex items-center gap-6">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary via-primary/90 to-accent flex items-center justify-center shadow-lg shadow-primary/30">
                <Wind className="h-5 w-5 text-white" />
              </div>
              <div className="absolute -bottom-1 -right-1 w-3.5 h-3.5 rounded-full bg-emerald-500 border-2 border-background animate-pulse-soft" />
            </div>
            <div className="hidden sm:block">
              <h1 className="display text-base font-semibold tracking-tight leading-tight">
                TinyDCS Explorer
              </h1>
              <p className="text-[11px] text-muted-foreground leading-tight">
                Altitude Decompression-Sickness Risk · Research Console
              </p>
            </div>
          </div>

          {/* Status chips */}
          <div className="hidden lg:flex items-center gap-2 ml-2">
            <span className="pill-primary">
              <span className="w-1.5 h-1.5 rounded-full bg-primary" />
              ADRAC v0.6.0
            </span>
            <span className="pill-accent">
              <span className="w-1.5 h-1.5 rounded-full bg-accent" />
              ECharts 6.x
            </span>
            <span className="pill-muted">
              closed-form R² 0.864 · n 15 908
            </span>
          </div>

          <div className="ml-auto flex items-center gap-1.5">
            <button
              onClick={() => setIsDark(!isDark)}
              aria-label="Toggle theme"
              className="p-2 rounded-lg text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
            >
              {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>
            <a
              href="https://github.com/strikerdlm/DCS"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Open repository"
              className="p-2 rounded-lg text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
            >
              <Github className="h-4 w-4" />
            </a>
          </div>
        </div>
      </header>

      {/* Main shell with rail */}
      <div className="flex-1">
        <div className="max-w-[1480px] mx-auto px-6 lg:px-8 py-6 grid lg:grid-cols-[260px_1fr] gap-6">
          {/* Left rail */}
          <aside className="hidden lg:block">
            <div className="sticky top-24">
              <div className="nav-rail">
                {NAV_GROUPS.map((group, gi) => (
                  <div key={group.heading}>
                    <div
                      className={cn(
                        "px-2 pb-1",
                        gi === 0 ? "pt-2" : "pt-3 mt-1 border-t border-border/50",
                      )}
                    >
                      <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                        {group.heading}
                      </p>
                    </div>
                    {group.items.map((item) => (
                      <button
                        key={item.id}
                        onClick={() => setActiveTab(item.id)}
                        className={cn(
                          "nav-link group w-full",
                          activeTab === item.id && "nav-link-active",
                        )}
                      >
                        <span
                          className={cn(
                            "h-8 w-8 rounded-lg flex items-center justify-center transition-colors",
                            activeTab === item.id
                              ? "bg-primary/15 text-primary ring-1 ring-primary/20"
                              : "bg-muted text-muted-foreground group-hover:text-foreground",
                          )}
                        >
                          {item.icon}
                        </span>
                        <div className="flex flex-col items-start min-w-0">
                          <span className="text-sm leading-tight">{item.label}</span>
                          <span className="text-[11px] text-muted-foreground/80 leading-tight truncate w-[160px]">
                            {item.description}
                          </span>
                        </div>
                      </button>
                    ))}
                  </div>
                ))}
              </div>

              {/* Rail card — mission ribbon */}
              <div className="surface-glass mt-4 p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                    Validity envelope
                  </span>
                  <Mountain className="h-3.5 w-3.5 text-muted-foreground" />
                </div>
                <ul className="text-[11px] space-y-1.5 text-muted-foreground">
                  <li className="flex justify-between gap-2">
                    <span>Altitude</span>
                    <span className="text-num text-foreground">18 – 40 kft</span>
                  </li>
                  <li className="flex justify-between gap-2">
                    <span>Prebreathe</span>
                    <span className="text-num text-foreground">0 – 180 min</span>
                  </li>
                  <li className="flex justify-between gap-2">
                    <span>Time at altitude</span>
                    <span className="text-num text-foreground">10 – 240 min</span>
                  </li>
                  <li className="flex justify-between gap-2">
                    <span>Exercise</span>
                    <span className="text-num text-foreground">Rest / Mild / Heavy</span>
                  </li>
                </ul>
                <p className="text-[11px] text-muted-foreground/80 border-t border-border/60 pt-2">
                  OOD detector abstains outside this envelope.
                </p>
              </div>
            </div>
          </aside>

          {/* Mobile rail */}
          <nav className="lg:hidden -mx-2 px-2 overflow-x-auto">
            <div className="flex gap-1.5 pb-2 min-w-max">
              {NAV_ITEMS.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={cn(
                    "flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium border transition-colors whitespace-nowrap",
                    activeTab === item.id
                      ? "bg-primary/10 text-primary border-primary/20"
                      : "border-border/50 text-muted-foreground hover:text-foreground hover:bg-muted",
                  )}
                >
                  {item.icon}
                  {item.label}
                </button>
              ))}
            </div>
          </nav>

          {/* Main panel */}
          <main className="min-w-0">
            <div key={activeTab} className="animate-in">
              {renderContent()}
            </div>
          </main>
        </div>
      </div>

      <footer className="border-t border-border/60 bg-card/40 backdrop-blur-md mt-12">
        <div className="max-w-[1480px] mx-auto px-6 lg:px-8 py-8 grid md:grid-cols-3 gap-8">
          <div>
            <h3 className="display text-sm font-semibold mb-2">TinyDCS</h3>
            <p className="text-[12.5px] text-muted-foreground leading-relaxed">
              Wearable-grade machine-learning stack for altitude decompression-sickness
              risk. Hybrid physics + ML, calibrated uncertainty, edge-deployable.
              Operationally honest.
            </p>
          </div>
          <div>
            <h3 className="display text-sm font-semibold mb-2">Models in this build</h3>
            <ul className="text-[12.5px] text-muted-foreground space-y-1">
              <li>· ADRAC log-logistic AFT (Pilmanis, 2004)</li>
              <li>· NASA Conkin RM/NM logistic (TM-2004-213093)</li>
              <li>· 3RUT-MBe1 schematic preview (NEDU TR 18-01)</li>
              <li>· EVA scenario simulator (NASA/ESA public assumptions)</li>
            </ul>
          </div>
          <div>
            <h3 className="display text-sm font-semibold mb-2">Documentation</h3>
            <ul className="text-[12.5px] text-muted-foreground space-y-1">
              <li>
                <code className="text-num text-[11px] text-foreground">docs/methods.md</code> —
                TRIPOD+AI methods M1–M8
              </li>
              <li>
                <code className="text-num text-[11px] text-foreground">docs/runbook.md</code> —
                step-by-step reproduction
              </li>
              <li>
                <code className="text-num text-[11px] text-foreground">docs/scientific-background.md</code> —
                model provenance and references
              </li>
            </ul>
          </div>
        </div>
        <div className="border-t border-border/60 py-4">
          <div className="max-w-[1480px] mx-auto px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-2 text-[11px] text-muted-foreground">
            <span>© {new Date().getFullYear()} TinyDCS · research artifact · MIT-adjacent license</span>
            <span className="text-num">v0.6.0 · build {new Date().toISOString().slice(0, 10)}</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
