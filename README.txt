# Data Book Generator Script

## Overview

This Python script is designed to generate an HTML data book for a set of digital IC cells in the tsmc180 technology library. The data book includes information such as cell names, functions, ports, dimensions, area, input capacitances, and propagation delays. The script uses the Magic VLSI Layout Tool and HSPICE for extraction and simulation.

## Prerequisites

Before using the script, ensure you have the following installed:

* Python 3
* Magic VLSI Layout Tool
* HSPICE

## Usage

1. Ensure your Magic cell files (`.mag`) are in the same directory as the script.
2. Run the following command to generate the data book:

        $ python3 script.py
        ...
        [PASS]  Script completed successfully

3. The script will process each cell, extract relevant information, and generate an HTML data book named `databook.html`.
4. Open the data book in you preffered web browser to view the results.

## Data Book Structure

The generated HTML data book provides detailed information about each cell, including:

* Cell Name
  * The name of the cell.
* Function
  * The function of the cell.
* Ports
  * A table containing the names, directions, and positions of each port in the cell.
* Input Capacitances
  * Input capacitance values for input ports.
  * If there are no input ports, this section is omitted.
* Propagation Delays
  * Propagation delay values for input ports with different load capacitances.
  * Again, if there are no input ports, this section is omitted.
* Dimensions
  * Width and height of the cell.
* Area
  * Area occupied by the cell.

## Logs

The script generates detailed logs in the `logs` directory, including:

* `all.log`: All log messages.
* `info.log`: Informational messages.
* `warnings.log`: Warning messages.
* `errors.log`: Error messages.

Review the logs to identify any warnings or errors during script execution.
