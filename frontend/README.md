# DCS Safety Dashboard - TypeScript Frontend

React + TypeScript interface for TinyDCS model exploration and space-operations scenario planning. The dashboard runs standalone against bundled data and browser-side calculation utilities; no backend is required for local exploration.

## Quick Start

```bash
npm install
npm run dev        # http://localhost:5173
npm run build      # production build in dist/
npm run preview
```

## Main Capabilities

### EVA Mission Simulator

Mission-planning screen for DCS-informed EVA trade studies. It includes three primary scenarios:

1. **Scenario A: Commercial stand-up EVA analog**
   - Short vehicle depressurization
   - Suit oxygen
   - Limited workload
   - Return and repressurization

2. **Scenario B: Artemis-relevant lunar EVA day**
   - Prebreathe and suit-pressure controls
   - 4-6 h lunar surface activity
   - Changing workload blocks
   - Dust, thermal, radiation, communications, and shelter-return controls

3. **Scenario C: Habitat pressure-management decision**
   - Compare scheduled EVA now against delayed EVA
   - Extended prebreathe option
   - Altered habitat oxygen/pressure profile
   - Risk trajectory and LxC decision category

For each scenario, the screen reports:

- point-risk trajectory over time;
- 95% interval trajectory over time;
- in-envelope or abstain flag;
- maximum risk and time of maximum risk;
- time-integrated risk;
- 5x5 likelihood x consequence category;
- decision implication: `proceed`, `monitor`, `modify`, `delay`, `abort`, or `abstain`;
- decision alternatives for prebreathe, suit pressure, habitat atmosphere, EVA duration, and workload.

The EVA screen also includes a multi-hazard matrix for DCS, hypoxia, CO2 retention, thermal strain, dust contamination, fatigue/injury, radiation event, and consumables margin.

### Model Explorer

The dashboard also includes model-focused views:

- **ADRAC-derived risk predictor** - interactive exposure inputs and feature-vector display.
- **Mechanistic 3RUT-MBe1 preview** - schematic time-series view for tissue gas and hazard-shape exploration.
- **NASA ETR logistic model** - Conkin RM/NM equations with age/sex covariates.
- **Validation dashboard** - closed-form ADRAC fit diagnostics, residuals, heatmaps, and worst-case cells.

### Visual Analytics

- ECharts-based risk gauges, heatmaps, scatter plots, timelines, histograms, and dose-response plots.
- Shared design tokens for light and dark mode.
- Responsive layout for desktop, tablet, and narrow mobile screens.
- Export-ready chart rendering through ECharts toolbox controls where enabled.

## Tech Stack

- React + TypeScript
- Vite
- ECharts / echarts-for-react
- TailwindCSS
- Radix UI primitives
- Lucide React icons

## Project Structure

```text
frontend/
├── src/
│   ├── components/
│   │   ├── eva/             # EVA scenario simulator
│   │   ├── charts/          # ECharts visualization components
│   │   ├── models/          # model-specific views
│   │   └── ui/              # reusable UI primitives
│   ├── data/                # presets, validation payloads, constants
│   ├── lib/                 # formatting and generic utilities
│   ├── types/               # TypeScript contracts
│   └── utils/               # model and EVA calculation utilities
├── public/
└── index.html
```

## Scientific and Technical Anchors

- Conkin, J. (2004). *Likelihood and severity of decompression sickness with exercise during EVA* (NASA/TM-2004-213093).
- Gerth, W. A., Doolette, D. J., & Gault, K. A. (2018). *A probabilistic model of altitude decompression sickness based on the 3RUT-MB model* (NEDU TR 18-01).
- NASA Life Support Baseline Values and Assumptions Document.
- NASA AxEMU and xEVAS public technical updates.
- ESA/DLR LUNA lunar analog facility public technical material.

## Configuration

Optional local environment variables:

```env
VITE_API_URL=http://localhost:8000
VITE_DEBUG=false
```

Customization points:

- Theme colors: `tailwind.config.js`
- Chart theme: `src/components/charts/chartConfig.ts`
- EVA scenarios: `src/data/evaScenarios.ts`
- Model defaults and validation data: `src/data/`

## License

This frontend is part of the TinyDCS repository. See the root `LICENSE` file for terms.
