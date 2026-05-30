/**
 * DCS Risk Model Types
 * 
 * Type definitions for the Decompression Sickness (DCS) Safety Dashboard
 * Aligned with scientific model specifications from research papers.
 */

// ============================================================================
// Common Types
// ============================================================================

export type ExerciseLevel = "Rest" | "Mild" | "Heavy";

export type RiskLevel = "low" | "moderate" | "high";

export interface RegressionMetrics {
  r2: number;
  mae: number;
  rmse: number;
  mse: number;
}

export interface ModelValidity {
  name: string;
  sources: string[];
  notesMd: string;
  metrics: Array<{ key: string; value: string }>;
}

// ============================================================================
// ML Surrogate Model Types
// ============================================================================

export interface MLSurrogateInputs {
  altitude: number; // feet
  timeAtAltitude: number; // minutes
  prebreathingTime: number; // minutes
  exerciseLevel: ExerciseLevel;
  extraFeatures?: Record<string, number>;
}

export interface MLSurrogatePrediction {
  riskPercent: number;
  features: Array<{ name: string; value: number }>;
  modelMetadata?: {
    scalerPath?: string;
    encoderPath?: string;
    modelPath?: string;
    applyV11Transforms?: boolean;
  };
}

// ============================================================================
// Mechanistic 3RUT-MBe1 Model Types
// ============================================================================

export interface ProfileSegment {
  durationMin: number;
  pAmbAtm: number;
  fio2: number;
  fin2: number;
  iExLMinWb: number; // Exercise intensity (L/min whole-body O2 above rest)
}

export interface MechanisticInputs {
  altitudeFt: number;
  timeAtAltitudeMin: number;
  prebreathingTimeMin: number;
  prebreathingExerciseLevel: ExerciseLevel;
  altitudeExerciseLevel: ExerciseLevel;
  prebreathFio2: number;
  breatheO2AtAltitude: boolean;
  ascentDurationMin: number;
  dtMin: number;
}

export interface ModelState {
  tMin: number;
  pAmbAtm: number;
  fio2: number;
  fin2: number;
  iExLMinWb: number;
  ptN2Atm: number;
  ptO2Atm: number;
  rHat: number;
  pbN2Atm: number;
  pbO2Atm: number;
  xHatN2: number;
  xHatO2: number;
  nB: number;
  nBMax: number;
  pCrushAtm: number;
  betaFHat: number;
  rHatMin: number;
  hPerMin: number;
  pSurvival: number;
  pDcs: number;
}

export interface MechanisticSimulationResult {
  history: ModelState[];
  finalPDcsPercent: number;
  segments: ProfileSegment[];
}

// ============================================================================
// NASA ETR Logistic Model Types
// ============================================================================

export type NASAVariant = "NM" | "RM";

export interface NASAInputs {
  variant: NASAVariant;
  p0Psia: number; // Initial tissue ppN2
  paPsia: number; // Ambient ppN2 during PB
  pbTimeMin: number; // Prebreathe duration
  vo2MlKgMin: number; // VO2 during PB
  lambda2: number; // λ2 parameter
  p2Psia: number; // Ambient pressure after depressurization
  sex: "Male" | "Female";
  ageYears: number;
}

export interface NASAPrediction {
  p1n2Psia: number; // Tissue N2 after prebreathe
  etr: number; // Exercise Tissue Ratio
  pDcsPercent: number;
  equation: string;
}

// ============================================================================
// Validation Types
// ============================================================================

export interface ValidationDataPoint {
  altitude: number;
  timeAtAltitude: number;
  prebreathingTime: number;
  exerciseLevel: string;
  riskOfDcs: number; // Reference risk %
  predictedRisk?: number;
  residual?: number;
  absError?: number;
}

export interface ValidationResult {
  metrics: RegressionMetrics;
  dataPoints: ValidationDataPoint[];
  totalRows: number;
  filteredRows: number;
}

export interface ValidationFilters {
  exerciseLevels: ExerciseLevel[];
  altitudeRange: [number, number];
  timeRange: [number, number];
  maxRows?: number;
}

// ============================================================================
// Chart Configuration Types
// ============================================================================

export interface ChartTheme {
  backgroundColor: string;
  textColor: string;
  gridColor: string;
  axisColor: string;
  tooltipBg: string;
  primaryColor: string;
  secondaryColor: string;
  tertiaryColor: string;
  riskLowColor: string;
  riskModerateColor: string;
  riskHighColor: string;
}

export interface TimeSeriesDataPoint {
  time: number;
  value: number;
  label?: string;
}

// ============================================================================
// Citation Types
// ============================================================================

export interface Citation {
  id: string;
  authors: string;
  title: string;
  year: number;
  doi?: string;
  url?: string;
  type: "article" | "report" | "book" | "software";
}
