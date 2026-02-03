import React, { useState } from "react";
import {
  MLSurrogate,
  Mechanistic3RUT,
  NASALogistic,
  ValidationDashboard,
} from "./components/models";
import { cn } from "./lib/utils";
import {
  Brain,
  Beaker,
  Rocket,
  BarChart3,
  Moon,
  Sun,
  AlertTriangle,
  ExternalLink,
  Github,
  Menu,
  X,
} from "lucide-react";

type ModelTab = "ml" | "mechanistic" | "nasa" | "validation";

function App(): React.ReactElement {
  const [activeTab, setActiveTab] = useState<ModelTab>("ml");
  const [isDark, setIsDark] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Toggle dark mode
  React.useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [isDark]);

  const tabs: { id: ModelTab; label: string; icon: React.ReactNode }[] = [
    { id: "ml", label: "ML Surrogate", icon: <Brain className="h-4 w-4" /> },
    {
      id: "mechanistic",
      label: "3RUT‑MBe1",
      icon: <Beaker className="h-4 w-4" />,
    },
    { id: "nasa", label: "NASA ETR", icon: <Rocket className="h-4 w-4" /> },
    {
      id: "validation",
      label: "Validation",
      icon: <BarChart3 className="h-4 w-4" />,
    },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case "ml":
        return <MLSurrogate />;
      case "mechanistic":
        return <Mechanistic3RUT />;
      case "nasa":
        return <NASALogistic />;
      case "validation":
        return <ValidationDashboard />;
      default:
        return <MLSurrogate />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50 dark:from-gray-950 dark:via-gray-900 dark:to-blue-950">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl">
        <div className="container mx-auto px-4">
          <div className="flex h-16 items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 text-white">
                <Beaker className="h-5 w-5" />
              </div>
              <div>
                <h1 className="text-lg font-bold tracking-tight">
                  DCS Safety Dashboard
                </h1>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Decompression Sickness Risk Models
                </p>
              </div>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center gap-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all",
                    activeTab === tab.id
                      ? "bg-primary/10 text-primary"
                      : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
                  )}
                >
                  {tab.icon}
                  {tab.label}
                </button>
              ))}
            </nav>

            {/* Right side controls */}
            <div className="flex items-center gap-2">
              {/* Theme toggle */}
              <button
                onClick={() => setIsDark(!isDark)}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                aria-label="Toggle theme"
              >
                {isDark ? (
                  <Sun className="h-5 w-5 text-amber-500" />
                ) : (
                  <Moon className="h-5 w-5 text-gray-600" />
                )}
              </button>

              {/* GitHub link */}
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                aria-label="GitHub repository"
              >
                <Github className="h-5 w-5" />
              </a>

              {/* Mobile menu button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
              >
                {mobileMenuOpen ? (
                  <X className="h-5 w-5" />
                ) : (
                  <Menu className="h-5 w-5" />
                )}
              </button>
            </div>
          </div>

          {/* Mobile Navigation */}
          {mobileMenuOpen && (
            <nav className="md:hidden py-4 border-t">
              <div className="flex flex-col gap-1">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => {
                      setActiveTab(tab.id);
                      setMobileMenuOpen(false);
                    }}
                    className={cn(
                      "flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all",
                      activeTab === tab.id
                        ? "bg-primary/10 text-primary"
                        : "text-gray-600 dark:text-gray-300"
                    )}
                  >
                    {tab.icon}
                    {tab.label}
                  </button>
                ))}
              </div>
            </nav>
          )}
        </div>
      </header>

      {/* Disclaimer Banner */}
      <div className="bg-amber-50 dark:bg-amber-900/20 border-b border-amber-200 dark:border-amber-800">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
            <div className="text-sm text-amber-800 dark:text-amber-200">
              <strong>Research Use Only:</strong> This dashboard is for academic
              and research purposes. Models are{" "}
              <strong>not validated</strong> for clinical, operational, or
              real-world risk decision-making. Do not use for planning flights,
              dives, EVAs, or medical care.
              <a
                href="#"
                className="ml-2 inline-flex items-center gap-1 text-amber-700 dark:text-amber-300 underline hover:no-underline"
              >
                Learn more <ExternalLink className="h-3 w-3" />
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {renderContent()}
      </main>

      {/* Footer */}
      <footer className="border-t bg-white/50 dark:bg-gray-900/50 mt-12">
        <div className="container mx-auto px-4 py-8">
          <div className="grid md:grid-cols-3 gap-8">
            {/* About */}
            <div>
              <h3 className="font-semibold mb-3">About This Dashboard</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                A comprehensive research UI for exploring multiple DCS risk model
                families. Built with React, TypeScript, and ECharts for
                publication-quality visualizations.
              </p>
            </div>

            {/* Model Families */}
            <div>
              <h3 className="font-semibold mb-3">Model Families</h3>
              <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-2">
                <li>• ML Surrogate (ADRAC-derived)</li>
                <li>• Mechanistic 3RUT‑MBe1 (NEDU TR 18-01)</li>
                <li>• NASA ETR Logistic (RM/NM)</li>
              </ul>
            </div>

            {/* References */}
            <div>
              <h3 className="font-semibold mb-3">Key References</h3>
              <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-2">
                <li>NEDU TR 18-01 (Gerth et al., 2018)</li>
                <li>NASA/TM-2004-213093 (Conkin, 2004)</li>
                <li>ASEM Vol. 75, No. 3 (2004)</li>
              </ul>
            </div>
          </div>

          <div className="mt-8 pt-8 border-t text-center text-sm text-gray-500">
            <p>
              © {new Date().getFullYear()} DCS Safety Dashboard. Built for Q1
              science journal publication quality.
            </p>
            <p className="mt-1 text-xs">
              All citations and references are verifiable through the linked
              repository documentation.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
