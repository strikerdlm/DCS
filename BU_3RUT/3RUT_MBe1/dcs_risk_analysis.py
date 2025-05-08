import pandas as pd
import matplotlib.pyplot as plt
import os

try:
    import seaborn as sns
except ImportError:
    sns = None


def main():
    # Load the CSV file containing the simulation grid results from the current folder
    file_path = os.path.join(os.path.dirname(__file__), 'simulation_grid_results.csv')
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"File {file_path} not found. Ensure simulation_grid_results.csv is in the current directory.")
        return

    # Print basic information about the data
    print("Data Info:")
    print(df.info())
    print("\nDescriptive Statistics:")
    print(df.describe())

    # Compute the correlation matrix
    corr = df.corr()
    print("\nCorrelation Matrix:")
    print(corr)

    # Plot the correlation heatmap using seaborn if available
    if sns is not None:
        plt.figure(figsize=(8, 6))
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f')
        plt.title('Correlation Heatmap of Flight Parameters')
        plt.tight_layout()
        plt.show()
    else:
        print('Seaborn not available. Skipping heatmap plot.')

    # Define independent variables to plot against risk_probability
    independent_vars = ['preox_duration', 'ascent_rate_ftmin', 'cruise_alt_ft', 'cruise_duration', 'total_flight_time', 'risk_index']

    # Create scatter plots: risk_probability vs each independent variable
    for var in independent_vars:
        plt.figure(figsize=(8, 5))
        plt.scatter(df[var], df['risk_probability'], alpha=0.7, edgecolor='k')
        plt.xlabel(var)
        plt.ylabel('Risk Probability')
        plt.title(f'Risk Probability vs {var}')
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    # If seaborn is available, produce a pairplot of all variables
    if sns is not None:
        sns.pairplot(df)
        plt.suptitle('Pairplot of DCS Flight Parameters and Risk', y=1.02)
        plt.show()
    else:
        print('Seaborn not available. Skipping pairplot.')


if __name__ == '__main__':
    main() 