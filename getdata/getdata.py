#!/usr/bin/env python3
"""
This script extracts the total energy and thermochemical data from Gaussian 09 or Gaussian 16 output files
and creates the results.csv file with extracted data.

Usage in GNU/Linux operating system command line:
1. chmod u+x  (one time only - making the file executable)
2. ./getdata.py file_name(s).log (run the script)
"""

__author__ = "Łukasz Fojcik"

import sys
from math import log
import csv

def Usage():
    """Print usage information and exit."""
    print(__doc__)
    sys.exit()

if len(sys.argv) == 1:
    Usage()

def parse(fle):
    """Parse Gaussian 09 or 16 log file and extract relevant data."""

    f = open(fle)

    e0 = 'SCF Done'
    vzpe = 'Zero-point correction'
    etot = 'Thermal correction to Energy'
    h = 'Thermal correction to Enthalpy'
    g = 'Thermal correction to Gibbs Free Energy'
    e0vzpe = 'Sum of electronic and zero-point Energies'
    e0etot = 'Sum of electronic and thermal Energies'
    e0h = 'Sum of electronic and thermal Enthalpies'
    e0g = 'Sum of electronic and thermal Free Energies'

    SCF = 0

    ## PRZYKŁAD 1
    while 1:
        l = f.readline()
        if l == '':
            break
        if l.find('- Thermochemistry -') != -1:
            break
        if l.find(e0) != -1:
            l = l.split('=')[-1]
            l = l.split()[0]
            SCF = l

    data = [fle.replace('.log', '').replace('_', '-')]
    data.append(SCF)

    while 1:
        l = f.readline()
        if l == '':
            break
        if l.find(vzpe) != -1:
            l = l.split('=')[1].strip().split()[0]
            data.append(l)
        elif l.find(etot) != -1:
            l = l.split('=')[1].strip().split()[0]
            data.append(l)
        elif l.find(h) != -1:
            l = l.split('=')[1].strip().split()[0]
            data.append(l)
        elif l.find(g) != -1:
            l = l.split('=')[1].strip().split()[0]
            data.append(l)
        elif l.find(e0vzpe) != -1:
            l = l.split('=')[1].strip().split()[0]
            data.append(l)
        elif l.find(e0etot) != -1:
            l = l.split('=')[1].strip().split()[0]
            data.append(l)
        elif l.find(e0h) != -1:
            l = l.split('=')[1].strip().split()[0]
            data.append(l)
        elif l.find(e0g) != -1:
            l = l.split('=')[1].strip().split()[0]
            data.append(l)

    f.close()

    return data

def write_data(csv_output, data, i):
    """ write_formatted_data to the .csv file """
    row = [float(data[i][j+1]) for j in range(len(data[i]) - 1)]
    row.append(data[i][0])
    csv_output.writerow(row)

data = []

# Calculate conversion factor
R = 8.3145   # J/mol*K (gas constant)
T = 298.15   # K (temperature)
P = 101325   # Pa (pressure)
cal = 4.1868 # J (calory to Joule conversion - units of energy)
RTlnV = R * T * log(R * T / (0.001 * P)) / cal

header = ['E(SCF)', 'VZPE', 'E_{tot}', 'H', 'G', 'E_{0}+VZPE', 'E_{0}+E_{tot}', 'E_{0}+H', 'E_{0}+G', 'File']

csvfile = open('results.csv', 'w', newline='')
csv_output = csv.writer(csvfile)
csv_output.writerow([f'# Conversion from gas-phase standard state to 1M is: {RTlnV/1000:4.3f} kcal/mol'])
csv_output.writerow(header)

for f in sys.argv[1:]:
    data.append(parse(f))

for i in range(len(data)):
    write_data(csv_output, data, i)

csvfile.close()
