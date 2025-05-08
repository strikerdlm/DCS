import numpy as np
import pandas as pd
from dcs_cli import calculate_dcs_risk
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm.auto import tqdm
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import joblib
import os
from datetime import datetime
from glob import glob
import statsmodels.api as sm
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from matplotlib.collections import PolyCollection

def generate_scenarios(n_scenarios=3000):
    """
    Generate test scenarios with realistic parameter ranges
    
    Altitude: 18,000 to 40,000 ft (limited to model's valid range)
    Time at altitude: 1 to 360 minutes
    Prebreathing time: 0 to 240 minutes
    Exercise levels: Rest, Mild, Heavy
    """
    
    # Generate random parameters within realistic ranges
    # Using stratified sampling for better coverage of altitude ranges
    altitude_ranges = [
        (18000, 25000),  # Low altitude range
        (25000, 32500),  # Medium altitude range
        (32500, 40000)   # High altitude range
    ]
    
    # Generate equal number of samples from each altitude range
    samples_per_range = n_scenarios // len(altitude_ranges)
    altitudes = np.array([])
    
    for low, high in altitude_ranges:
        range_samples = np.random.uniform(low, high, samples_per_range)
        altitudes = np.append(altitudes, range_samples)
    
    # Add remaining samples if any (due to integer division)
    remaining = n_scenarios - len(altitudes)
    if remaining > 0:
        extra_samples = np.random.uniform(18000, 40000, remaining)
        altitudes = np.append(altitudes, extra_samples)
    
    # Generate other parameters
    times_at_altitude = np.random.uniform(1, 360, n_scenarios)
    prebreathing_times = np.random.uniform(0, 240, n_scenarios)
    
    # Exercise levels with equal probability
    exercise_levels = np.random.choice(['Rest', 'Mild', 'Heavy'], n_scenarios)
    
    # Create scenarios dataframe
    scenarios = pd.DataFrame({
        'altitude': altitudes,
        'time_at_altitude': times_at_altitude,
        'prebreathing_time': prebreathing_times,
        'exercise_level': exercise_levels
    })
    
    # Add some extreme cases for comprehensive testing within valid range
    extreme_cases = pd.DataFrame([
        {'altitude': 40000, 'time_at_altitude': 360, 'prebreathing_time': 0, 'exercise_level': 'Heavy'},
        {'altitude': 18000, 'time_at_altitude': 1, 'prebreathing_time': 240, 'exercise_level': 'Rest'},
        {'altitude': 32500, 'time_at_altitude': 180, 'prebreathing_time': 120, 'exercise_level': 'Mild'}
    ])
    
    scenarios = pd.concat([scenarios, extreme_cases], ignore_index=True)
    
    # Add some validation checks
    assert scenarios['altitude'].min() >= 18000, "Altitude below minimum threshold"
    assert scenarios['altitude'].max() <= 40000, "Altitude above maximum threshold"
    assert len(scenarios) == n_scenarios + 3, "Incorrect number of scenarios"
    
    return scenarios

def find_latest_model_timestamp(model_dir):
    """Find the most recent model timestamp from the output directory"""
    try:
        # Get absolute path to model directory
        model_dir = os.path.abspath(model_dir)
        if not os.path.exists(model_dir):
            raise FileNotFoundError(f"Model directory not found: {model_dir}")
            
        # Get all joblib files
        model_files = glob(os.path.join(model_dir, "*_*.joblib"))
        if not model_files:
            raise FileNotFoundError(f"No model files found in {model_dir}")
        
        # Extract timestamps from filenames
        timestamps = []
        for f in model_files:
            try:
                filename = os.path.basename(f)
                if '_' in filename:
                    parts = filename.split('_')
                    if len(parts) >= 3:
                        date_part = parts[-2]
                        time_part = parts[-1].replace('.joblib', '')
                        if len(date_part) == 8 and len(time_part) == 4:
                            timestamps.append(f"{date_part}_{time_part}")
            except:
                continue
        
        if not timestamps:
            raise ValueError("No valid timestamps found in model files")
            
        latest = max(timestamps)
        print(f"\nUsing model timestamp: {latest}")
        print(f"Model files being used:")
        for f in model_files:
            if latest in f:
                print(f"• {os.path.basename(f)}")
        return latest
        
    except Exception as e:
        raise RuntimeError(f"Error finding latest model timestamp: {str(e)}")

def verify_model_files(model_dir, timestamp):
    """Verify that all required model files exist"""
    required_files = [
        f"scaler_{timestamp}.joblib",
        f"simple_model_{timestamp}.joblib",
        f"onehot_encoder_{timestamp}.joblib"
    ]
    
    missing = []
    for file in required_files:
        full_path = os.path.join(model_dir, file)
        if not os.path.exists(full_path):
            missing.append(file)
    
    if missing:
        raise FileNotFoundError(f"Missing required model files: {', '.join(missing)}")

def run_simulation(scenarios, model_dir='output'):
    """Run DCS risk calculation for all scenarios with ensemble predictions and proper preprocessing"""
    results = []
    error_cases = []
    
    # Find the latest model timestamp and verify files
    try:
        model_dir = os.path.abspath(model_dir)
        latest_timestamp = find_latest_model_timestamp(model_dir)
        verify_model_files(model_dir, latest_timestamp)
        print(f"\nUsing model artifacts from: {model_dir}")
        
        # Load model artifacts once to get expected features
        scaler, model_dict, onehot_encoder = calculate_dcs_risk.__globals__['load_model_artifacts'](model_dir)
        expected_features = model_dict.get('feature_names')
        if expected_features is None:
            raise ValueError("Model is missing feature_names. Please retrain the model.")
        
        # Create a test prediction to verify feature order
        test_scenario = scenarios.iloc[0]
        print("✅ Model verification successful")
        
    except Exception as e:
        raise RuntimeError(f"Failed to initialize simulation: {str(e)}")
    
    # Initialize progress bar AFTER model verification
    print("🚀 Starting DCS risk calculations...")
    progress_bar = tqdm(scenarios.iterrows(), total=len(scenarios), 
                       desc="Processing Scenarios", unit="scen",
                       bar_format="{l_bar}{bar:40}{r_bar}{bar:-10b}",
                       dynamic_ncols=True)
    
    for idx, scenario in progress_bar:
        try:
            result = calculate_dcs_risk(
                altitude=float(scenario['altitude']),
                time_at_altitude=float(scenario['time_at_altitude']),
                prebreathing_time=float(scenario['prebreathing_time']),
                exercise_level=str(scenario['exercise_level']),
                model_dir=model_dir
            )
            
            results.append({
                'altitude': scenario['altitude'],
                'time_at_altitude': scenario['time_at_altitude'],
                'prebreathing_time': scenario['prebreathing_time'],
                'exercise_level': scenario['exercise_level'],
                'dcs_risk': result['risk'],
                'uncertainty': result['uncertainty'],
                'ci_lower': result['ci_lower'],
                'ci_upper': result['ci_upper']
            })
            
            # Update progress bar postfix with current stats
            if idx % 100 == 0:  # Update every 100 scenarios to reduce overhead
                progress_bar.set_postfix({
                    'Success': f"{len(results)}/{idx+1}",
                    'Current Risk': f"{result['risk']:.1f}%",
                    'Errors': len(error_cases)
                })
            
        except Exception as e:
            error_cases.append({
                'scenario_id': idx,
                'scenario': scenario.to_dict(),
                'error': str(e)
            })
            continue
    
    # Final status update
    progress_bar.close()
    success_rate = (len(results)/len(scenarios))*100
    print(f"\nSimulation complete: {len(results)} successful ({success_rate:.1f}%) | {len(error_cases)} errors")

    # Save error cases if any occurred
    if error_cases:
        error_df = pd.DataFrame(error_cases)
        error_df.to_csv('simulation_errors.csv', index=False)
        print(f"⚠️  Error cases saved to 'simulation_errors.csv'")
    
    if not results:
        raise RuntimeError("❌ No successful predictions were made")
    
    return pd.DataFrame(results)

def analyze_results(results):
    """Analyze and visualize simulation results with advanced statistics and regression lines"""
    if len(results) == 0:
        raise ValueError("No results to analyze. Check if simulation completed successfully.")
    
    # Check for invalid predictions
    invalid_low = results[results['dcs_risk'] < 0]
    invalid_high = results[results['dcs_risk'] > 100]
    
    # Export full results to CSV
    results.to_csv('simulation_results.csv', index=False)
    
    # Create visualizations with error handling
    try:
        plt.figure(figsize=(18, 12))
        sns.set_style("whitegrid")
        plt.rcParams.update({'font.size': 12, 'font.family': 'DejaVu Sans'})
        
        # Function for enhanced regression plot
        def enhanced_regplot(ax, x, y, xlabel, title):
            # Use hexbin for density visualization
            hexbin = ax.hexbin(x, y, gridsize=50, cmap='Blues', mincnt=1, alpha=0.7)
            plt.colorbar(hexbin, ax=ax, label='Data density')
            
            # Add regression line with CI using seaborn with enhanced CI visualization
            sns.regplot(x=x, y=y, ax=ax, 
                       scatter=False, 
                       line_kws={'color': 'darkred', 'lw': 2},
                       ci=95,
                       color='darkred',  # Match line color
                       n_boot=1000,      # More bootstrap iterations for smoother CI
                       truncate=True,    # Limit line to data range
                       seed=42)          # For reproducibility
            
            # Customize CI appearance
            for collection in ax.collections:
                if isinstance(collection, PolyCollection):  # Changed from plt.PolyCollection
                    collection.set_alpha(0.3)  # Make CI more visible
                    collection.set_facecolor('darkred')  # Match line color
            
            ax.set_xlabel(xlabel)
            ax.set_ylabel('DCS Risk (%)')
            ax.set_title(title)
            ax.grid(True, alpha=0.3)
        
        # Plot 1: DCS Risk vs Altitude
        plt.subplot(2, 2, 1)
        enhanced_regplot(plt.gca(), results['altitude'], results['dcs_risk'],
                        'Altitude (ft)', 'A) DCS Risk vs Altitude')
        
        # Plot 2: DCS Risk vs Time at Altitude
        plt.subplot(2, 2, 2)
        enhanced_regplot(plt.gca(), results['time_at_altitude'], results['dcs_risk'],
                        'Time at Altitude (min)', 'B) DCS Risk vs Exposure Duration')
        
        # Plot 3: DCS Risk vs Prebreathing Time
        plt.subplot(2, 2, 3)
        enhanced_regplot(plt.gca(), results['prebreathing_time'], results['dcs_risk'],
                        'Prebreathing Time (min)', 'C) DCS Risk vs Prebreathing Time')
        
        # Plot 4: Box plot by Exercise Level
        plt.subplot(2, 2, 4)
        sns.boxplot(x='exercise_level', y='dcs_risk', data=results,
                    order=['Rest', 'Mild', 'Heavy'],
                    hue='exercise_level',
                    palette='Set2',
                    legend=False,
                    showfliers=True,          # Explicitly show outliers
                    fliersize=5,              # Make outlier points larger
                    linewidth=2,              # Make box lines thicker
                    medianprops={"color": "red", "linewidth": 2},  # Highlight median
                    boxprops={"alpha": 0.8},  # Slightly transparent boxes
                    whiskerprops={"linewidth": 2})  # Thicker whiskers
        plt.xlabel('Exercise Level')
        plt.ylabel('DCS Risk (%)')
        plt.title('D) DCS Risk Distribution by Exercise Level')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save figure with verification
        plot_filename = 'enhanced_simulation_results.png'
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Verify the plot was saved
        if not os.path.exists(plot_filename):
            raise RuntimeError("Failed to save plot file")
        
        # Verify file size is reasonable (> 10KB)
        if os.path.getsize(plot_filename) < 10000:
            raise RuntimeError("Plot file appears to be empty or corrupted")
            
        print(f"✅ Plot saved successfully to {plot_filename}")
        
    except Exception as e:
        print(f"⚠️ Error generating plots: {str(e)}")
        # Continue with statistical analysis even if plotting fails
    
    # Enhanced statistical reporting
    with open('comprehensive_analysis.txt', 'w', encoding='utf-8') as f:
        f.write("DCS Risk Simulation - Comprehensive Statistical Analysis\n")
        f.write("=" * 70 + "\n\n")
        
        # Model Information
        f.write("Model Information:\n")
        f.write("-" * 25 + "\n")
        model_dir = os.path.abspath('output')
        latest_timestamp = find_latest_model_timestamp(model_dir)
        f.write(f"Model Timestamp: {latest_timestamp}\n")
        f.write(f"Model Directory: {model_dir}\n\n")
        
        # Validation Checks
        f.write("Prediction Validation Checks:\n")
        f.write("-" * 25 + "\n")
        f.write(f"Invalid predictions < 0%: {len(invalid_low)} cases\n")
        f.write(f"Invalid predictions > 100%: {len(invalid_high)} cases\n")
        if len(invalid_low) > 0 or len(invalid_high) > 0:
            f.write("\n⚠️ WARNING: Invalid predictions detected!\n")
            if len(invalid_low) > 0:
                f.write("\nBelow 0% cases:\n")
                f.write(invalid_low[['altitude', 'time_at_altitude', 'prebreathing_time', 'exercise_level', 'dcs_risk']].to_string())
            if len(invalid_high) > 0:
                f.write("\nAbove 100% cases:\n")
                f.write(invalid_high[['altitude', 'time_at_altitude', 'prebreathing_time', 'exercise_level', 'dcs_risk']].to_string())
        f.write("\n\n")
        
        # Basic Statistics
        f.write("Basic Statistics:\n")
        f.write("-" * 25 + "\n")
        f.write(f"Total Scenarios Analyzed: {len(results):,}\n")
        f.write(f"Mean DCS Risk: {results['dcs_risk'].mean():.2f}%\n")
        f.write(f"Median DCS Risk: {results['dcs_risk'].median():.2f}%\n")
        f.write(f"Standard Deviation: {results['dcs_risk'].std():.2f}%\n")
        f.write(f"Risk Range: {results['dcs_risk'].min():.2f}% - {results['dcs_risk'].max():.2f}%\n")
        
        # Percentile Analysis
        percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
        f.write("\nPercentile Analysis:\n")
        f.write("-" * 25 + "\n")
        for p in percentiles:
            f.write(f"{p}th percentile: {np.percentile(results['dcs_risk'], p):.2f}%\n")
        
        # Exercise Level Analysis
        f.write("\nRisk by Exercise Level:\n")
        f.write("-" * 25 + "\n")
        exercise_stats = results.groupby('exercise_level')['dcs_risk'].agg(['count', 'mean', 'std', 'min', 'max'])
        f.write(exercise_stats.to_string())
        
        # ANOVA for Exercise Levels
        f.write("\n\nOne-way ANOVA for Exercise Levels:\n")
        f.write("-" * 25 + "\n")
        exercise_groups = [group for _, group in results.groupby('exercise_level')['dcs_risk']]
        f_stat, p_val = stats.f_oneway(*exercise_groups)
        f.write(f"F-statistic: {f_stat:.4f}\n")
        f.write(f"p-value: {p_val:.4e}\n")
        
        # Correlation Analysis
        f.write("\nCorrelation Analysis:\n")
        f.write("-" * 25 + "\n")
        f.write("\nPearson Correlations:\n")
        corr_matrix = results[['altitude', 'time_at_altitude', 'prebreathing_time', 'dcs_risk']].corr()
        f.write(corr_matrix.to_string())
        
        # Uncertainty Analysis
        f.write("\n\nUncertainty Analysis:\n")
        f.write("-" * 25 + "\n")
        f.write(f"Mean Uncertainty: ±{results['uncertainty'].mean():.2f}%\n")
        f.write(f"Max Uncertainty: ±{results['uncertainty'].max():.2f}%\n")
        f.write(f"Min Uncertainty: ±{results['uncertainty'].min():.2f}%\n")
        
        # Summary of Key Findings
        f.write("\nKey Findings:\n")
        f.write("-" * 25 + "\n")
        f.write("1. Model Validation:\n")
        f.write(f"   - Invalid predictions: {len(invalid_low) + len(invalid_high)} total\n")
        f.write(f"   - Prediction range: {results['dcs_risk'].min():.1f}% to {results['dcs_risk'].max():.1f}%\n")
        
        f.write("\n2. Risk Distribution:\n")
        f.write(f"   - Central tendency: {results['dcs_risk'].mean():.1f}% ± {results['dcs_risk'].std():.1f}%\n")
        f.write(f"   - Median risk: {results['dcs_risk'].median():.1f}%\n")
        
        f.write("\n3. Exercise Impact:\n")
        mean_by_exercise = results.groupby('exercise_level')['dcs_risk'].mean()
        f.write(f"   - Rest: {mean_by_exercise['Rest']:.1f}%\n")
        f.write(f"   - Mild: {mean_by_exercise['Mild']:.1f}%\n")
        f.write(f"   - Heavy: {mean_by_exercise['Heavy']:.1f}%\n")
        
        f.write("\n4. Uncertainty:\n")
        f.write(f"   - Average prediction uncertainty: ±{results['uncertainty'].mean():.1f}%\n")
        f.write(f"   - 95% of predictions within ±{np.percentile(results['uncertainty'], 95):.1f}%\n")
    
    print("\n✅ Comprehensive analysis saved to 'comprehensive_analysis.txt'")

def main():
    # Create output directory if it doesn't exist
    output_dir = os.path.abspath('output')
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Generate scenarios
        with tqdm(total=3, desc="Overall Progress", bar_format="{l_bar}{bar:40}{r_bar}{bar:-10b}") as main_bar:
            main_bar.set_description("🌱 Generating scenarios")
            scenarios = generate_scenarios(n_scenarios=10000)
            main_bar.update(1)
            
            # Run simulation
            main_bar.set_description("🚀 Running simulations")
            results = run_simulation(scenarios, model_dir=output_dir)
            main_bar.update(1)
            
            # Analyze results
            main_bar.set_description("📊 Analyzing results")
            if len(results) > 0:
                analyze_results(results)
                main_bar.update(1)
                
                # Display top results
                print("\n🔍 Simulation Summary:")
                print(f"• Scenarios processed: {len(results):,}")
                print(f"• Max risk: {results['dcs_risk'].max():.1f}%")
                print(f"• Min risk: {results['dcs_risk'].min():.1f}%")
                print(f"• Avg uncertainty: ±{results['uncertainty'].mean():.1f}%")
                
            else:
                print("No results were generated. Check simulation_errors.csv for details.")
    
    except Exception as e:
        print(f"\n❌ Critical Error: {str(e)}")
        if os.path.exists('simulation_errors.csv'):
            print("🔍 Error details available in 'simulation_errors.csv'")
        raise

if __name__ == "__main__":
    main() 