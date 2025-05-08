3RUT-MBe1 DCS Risk Model
=========================

Overview:
---------
This Python project implements a production‐quality version of the 3RUT-MBe1 model
for predicting decompression sickness (DCS) risk. The model features advanced 
nucleation kinetics, dynamic alveolar gas exchange with adaptive integration, 
mole-based tracking, support for multi-compartment and multiple bubble-size groups,
checkpointing, and comprehensive unit tests.

The main program file is:
   3RUT_MBe1/dcs_risk_model.py

Prerequisites:
--------------
- Python 3.6 or later
- Required Python packages:
    * matplotlib (for plotting)
    * numba (for just-in-time compilation)
    * scipy (for the calibration routine, if used)
    
You can install these packages using pip. For example:
    pip install matplotlib numba scipy

If any of the packages are missing, the code will still run (with reduced functionality,
e.g., no plotting if matplotlib is not installed).

Running the Code:
-----------------
1. Command-line Help:
   Run the following command to view all options:
       python 3RUT_MBe1/dcs_risk_model.py --help
       
   This will print a usage message listing all command-line options.

2. Running Unit Tests and Simulation:
   By default, when you run the code, a suite of unit tests will execute first.
   Once the tests pass, the main simulation will run. To run the simulation, use:
       python 3RUT_MBe1/dcs_risk_model.py
       
   The program will then print the final risk probability. If the '--plot' option is used,
   a plot window will display the simulation output (if matplotlib is installed).

Command-Line Options:
---------------------
--dt <float>
    Specify the initial time step in minutes (default is 0.1).
    
--simulation_time <float>
    Specify the total simulation time in minutes. If not set, the simulation runs for the full 
    duration defined by the flight profile.

--num_bubble_groups <int>
    Set the number of bubble-size groups to use in the simulation (default is 1).
    
--advanced_tissue_tracking
    Use advanced tissue mole tracking (flag; default off).

--advanced_alveolar
    Use the advanced alveolar gas exchange model (flag; default off).
    
--advanced_nucleation
    Use the simplified version of advanced nucleation kinetics (flag; default off).

--advanced_nucleation_full
    Use the full dynamic nucleation kinetics (placeholder implementation of Eqs. C.6–C.10) (flag; default off).

--config_file <string>
    Path to a JSON configuration file which can override default model parameters. The default is
    "model_config.json". (Place your config file in the same folder, if needed.)

--model_mode <string>
    Specify the simulation mode:
       "single" - Run simulation with a single tissue compartment (default)
       "multi"  - Run multi-compartment simulation and aggregate hazard indices.
       
--plot
    If specified, the simulation will display plots of the tissue nitrogen pressure, bubble number,
    and hazard index over time (requires matplotlib).

Examples:
---------
1. To run the simulation with default settings:
       python 3RUT_MBe1/dcs_risk_model.py

2. To run the simulation with an initial time step of 0.05 minutes, advanced alveolar exchange,
   and display plots:
       python 3RUT_MBe1/dcs_risk_model.py --dt 0.05 --advanced_alveolar --plot

3. To run a multi-compartment simulation with 2 bubble groups:
       python 3RUT_MBe1/dcs_risk_model.py --model_mode multi --num_bubble_groups 2

4. To specify a configuration file to override parameters:
       python 3RUT_MBe1/dcs_risk_model.py --config_file my_config.json
   
Notes:
------
- The unit tests run on startup and will log results to the console.
- The advanced RKF45 adaptive integration step is implemented and has a unit test.
- Many aspects of the complete model (e.g., multi-dimensional PDE solvers, full molecular 
  calibrations) are placeholders or stubs intended for further refinement.
- Please review and update the JSON configuration file (if used) to match your custom parameters.

Contact:
--------
For further information or assistance, please contact [Your Contact Info].

Happy Modeling!