# DCS Safety Dashboard - TypeScript Frontend

A modern, publication-quality TypeScript frontend for the Decompression Sickness (DCS) Risk Explorer. Built with React, ECharts, and TailwindCSS for Q1 science journal-ready visualizations.

## 🚀 Quick Start

This React + TypeScript dashboard is the **current / active** interface for the
project. The Streamlit app at the repository root (`apps/streamlit/`) is
**legacy** and superseded by this frontend.

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 📊 Features

### Model Families

1. **ML Surrogate (ADRAC-derived dataset)**
   - Supervised ML regression surrogate
   - Real-time risk prediction
   - Interactive parameter inputs
   - Feature vector visualization

2. **Mechanistic 3RUT‑MBe1**
   - Time-dependent bubble-evolution model
   - Based on NEDU TR 18‑01 (Appendix C/D)
   - Multi-panel time-series charts
   - CSV export functionality

3. **NASA ETR Logistic (RM/NM)**
   - Implements published equations from NASA/TM-2004-213093
   - NM (Eq. 14): ETR + sex covariate
   - RM (Eq. 15): ETR + age covariate
   - Real-time calculation with equation display

4. **ADRAC Validation Dashboard**
   - Predicted vs reference scatter plots
   - Residual distribution analysis
   - Error heatmaps by parameter region
   - Worst-case identification table

### Visualization Features

- **Publication-Quality Charts**: ECharts configurations optimized for Q1 science journals
- **Professional Color Palettes**: Print-compatible, colorblind-friendly schemes
- **Interactive Exploration**: Zoom, pan, filter, and export capabilities
- **Dark Mode Support**: Full dark/light theme support
- **Responsive Design**: Works on desktop and tablet

## 🛠 Tech Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Charts**: ECharts / echarts-for-react
- **Styling**: TailwindCSS + custom design tokens
- **UI Components**: Radix UI primitives
- **Icons**: Lucide React

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── charts/          # ECharts visualization components
│   │   │   ├── RiskGauge.tsx
│   │   │   ├── ScatterPlot.tsx
│   │   │   ├── TimeSeriesChart.tsx
│   │   │   ├── Heatmap.tsx
│   │   │   ├── Histogram.tsx
│   │   │   └── chartConfig.ts
│   │   ├── models/          # Model-specific components
│   │   │   ├── MLSurrogate.tsx
│   │   │   ├── Mechanistic3RUT.tsx
│   │   │   ├── NASALogistic.tsx
│   │   │   ├── ValidationDashboard.tsx
│   │   │   └── ValidityPanel.tsx
│   │   └── ui/              # Reusable UI components
│   ├── data/                # Mock data and constants
│   ├── hooks/               # Custom React hooks
│   ├── lib/                 # Utility functions
│   ├── types/               # TypeScript type definitions
│   └── utils/               # Model calculation utilities
├── public/
└── index.html
```

## 📚 Scientific References

The references below are formatted in APA 7th edition. Where source metadata
(volume, issue, pages, DOI) is not available in this repository, entries are
formatted as closely as the available information allows.

Conkin, J. (2004). *Likelihood and severity of decompression sickness with exercise during EVA* (NASA/TM-2004-213093). National Aeronautics and Space Administration. *(Source for the ETR logistic models, Eq. 14 and Eq. 15.)*

Gerth, W. A., Doolette, D. J., & Gault, K. A. (2018). *A probabilistic model of altitude decompression sickness based on the 3RUT-MB model* (NEDU TR 18-01). U.S. Navy Experimental Diving Unit. *(Used for the Mechanistic 3RUT-MBe1 implementation.)*

Information about venous gas emboli improves prediction of hypobaric decompression sickness. (2004). *Aviation, Space, and Environmental Medicine, 75*(3). *(Validation-methodology reference.)*

### Provenance

All equations and model parameters are documented with their original sources.
The validity panel for each model shows:
- Repository source files
- Available validation metrics
- Known limitations
- Applicable input ranges

## ⚠️ Disclaimer

**Research Use Only**: This dashboard is for academic and research purposes. Models are **NOT validated** for clinical, operational, or real-world risk decision-making.

- Do NOT use for planning flights, dives, EVAs, or medical care
- Do NOT use for personal risk assessment
- Consult qualified professionals for operational decisions

## 🎨 Design Principles

### For Publication-Quality Output

1. **Typography**: Inter font family for clarity
2. **Colors**: High-contrast schemes for print
3. **Axis Labels**: Scientific notation where appropriate
4. **Export**: High-DPI PNG export (3x pixel ratio)
5. **Legends**: Clear, non-overlapping legends

### Accessibility

- WCAG 2.1 AA compliant contrast ratios
- Keyboard navigation support
- Screen reader-friendly structure
- Colorblind-safe palettes available

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file for local configuration:

```env
# API endpoint for backend (optional - uses mock data by default)
VITE_API_URL=http://localhost:8000

# Enable debug mode
VITE_DEBUG=false
```

### Customization

- **Theme colors**: Edit `tailwind.config.js`
- **Chart themes**: Edit `src/components/charts/chartConfig.ts`
- **Model defaults**: Edit `src/data/mockData.ts`

## 📄 License

This frontend is part of the DCS research project. See the main repository LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

Built with ❤️ for the scientific community
