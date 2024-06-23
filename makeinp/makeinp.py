#!/usr/bin/env python3
"""
This script generates Gaussian or Gamess US input files from structural .xyz files. The script requires external .tmpl files.

Usage in GNU/Linux operating system command line: ./makeinp.py [options] .xyz file(s) (After the file has been granted the execution rights.)

Options:
  -h, --help       show this help
  -s, --gaussian   prepare gaussian inputs (expects gaussian.tmpl)
  -g, --gamess     prepare gamess inputs (expects gamess.tmpl)
"""

__author__  = "Łukasz Fojcik"

# Import necessary modules
import os, sys, getopt, re

from string import Template

# Regular expressions
reflags = re.DOTALL

#----------------------------------------------------------------------------
# Usage
#----------------------------------------------------------------------------
def Usage():
    """Print usage information and exit."""
    print(__doc__)
    sys.exit()

#----------------------------------------------------------------------------
# Main
#----------------------------------------------------------------------------
def Main(argv):
    '''Parse commandline and loop throught the logs'''


    # Set up defaults
    gaussian = 0
    gamess = 0

    # Parse commandline
    try:
        opts, args = getopt.getopt(argv, "hsg",
                                        ["help",
                                         "gaussian",
                                         "gamess",
                                         ])
    except getopt.GetoptError as error:
        print(error)
        Usage()
    if not argv:
        Usage()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            Usage()
        elif opt in ("-s", "--gaussian"):
            gaussian = 1
        elif opt in ("-g", "--gamess"):
            gamess = 1
    # Parse each data file (with xyz coords)
    data_files = args

    # Prepare inputs
    for f in data_files:
        if gaussian:
            GAUSSIAN_INPUTS(f)
        if gamess:
            GAMESS_INPUTS(f)

#----------------------------------------------------------------------------
# Common input template routines
#----------------------------------------------------------------------------
class INPUT_TEMPLATE(Template):
    delimiter = '@'

class INPUTS:
    """Common input routines"""
    def __init__(self, data):
        self.data = data

        self.ReadTemplate()

    def ReadTemplate(self):
        """Read or punch standard template"""
        try:
            self.tmpl = open(self.pkg + '.tmpl', 'r').read()
            self.tmpl = INPUT_TEMPLATE(self.tmpl)
            self.WriteInputs()
        except IOError:
            print("There's no " + self.pkg + " template. Please provide a " + self.pkg + ".tmpl file.")
            sys.exit()
        except AttributeError:
            pass

    def WriteInputs(self):
        pass

#----------------------------------------------------------------------------
# Gaussian routines
#----------------------------------------------------------------------------

class GAUSSIAN_INPUTS(INPUTS):
    """Gaussian 09 input routines"""

    def __init__(self, data):
        # template name
        self.pkg = "gaussian"
        super().__init__(data)

    def WriteInputs(self):

        # read xyz file
        try:
            xyz = open(self.data, 'r').readlines()
            xyz = xyz[2:int(xyz[0]) + 2]
            xyz = ''.join(xyz)
        except ValueError:
            print("Problem with *.xyz file?")
            sys.exit(1)

        else:
            filename = self.data.replace('.xyz', '')
            filename = filename.replace(' ', '_')
            finput = self.tmpl.substitute(data=xyz, chk=filename + '.chk')
            open(filename + '.inp', 'w').write(finput)

# ----------------------------------------------------------------------------
# Gamess (US) routines
# ----------------------------------------------------------------------------

class GAMESS_INPUTS(INPUTS):
    """Gamess US input routines"""

    def __init__(self, data):
        # template name
        self.pkg = "gamess"
        super().__init__(data)

    def WriteInputs(self):

        # initialize periodic table
        p = Periodic(0)

        # read xyz file
        try:
            xyz = open(self.data, 'r').readlines()
            xyz = xyz[2:int(xyz[0]) + 2]
        except ValueError:
            print("Problem with *.xyz file?")
            sys.exit(1)

        for i in range(len(xyz)):
            xyz[i] = xyz[i].split()
            xyz[i].insert(1, str(Atomn(xyz[i][0], p)))
            xyz[i] = '{:5} {:5} {:15} {:15} {:15}\n'.format(*xyz[i][:5])

        xyz.insert(0, ' $data\n%s\nc1 0\n' % self.data)
        xyz.append(' $end')
        xyz = ''.join(xyz)

        # write input files
        filename = self.data.replace('.xyz', '')
        filename = filename.replace(' ', '_')
        finput = self.tmpl.substitute(data=xyz)

        open(filename + '.inp', 'w').write(finput)

#----------------------------------------------------------------------------
# Utilities
#----------------------------------------------------------------------------

def Run(program, args):
    '''Run shell command'''
    os.system(program + ' ' + args)

def SkipLines(open_file, n):
    '''Read n lines from file f.'''

    for i in range(n):
        line = open_file.readline()
        if line == '':
            break

    return line

def FindLine(open_file, pattern):
    '''Read lines until pattern matches.'''

    while 1:
        line = open_file.readline()
        if line.find(pattern) != -1:
            break
        if line == '':
            line = -1
            break

    return line

def ReFindLine(open_file, pattern):
    '''Read lines until pattern matches.'''

    while 1:
        line = open_file.readline()
        if re.search(pattern, line) != None:
            break
        if line == '':
            line = -1
            break

    return line

def Periodic(mendeleiev):
    '''Returns the mendeleiev table as a Python list of tuples. Each cell
    contains either None or a tuple (symbol, atomic number), or a list of pairs
    for the cells * and **. Requires: "import re". Source: Gribouillis at
    www.daniweb.com - 2008 '''

    # L is a consecutive list of tuples ('Symbol', atomic number)
    L = [(e, i + 1) for (i, e) in enumerate(re.compile("[A-Z][a-z]*").findall('''
    HHeLiBeBCNOFNeNaMgAlSiPSClArKCaScTiVCrMnFeCoNiCuZnGaGeAsSeBrKr
    RbSrYZrNbMoTcRuRhPdAgCdInSnSbTeIXeCsBaLaCePrNdPmSmEuGdTbDyHoEr
    TmYbLuHfTaWReOsIrPtAuHgTlPbBiPoAtRnFrRaAcThPaUNpPuAmCmBkCfEsFm
    MdNoLrRfDbSgBhHsMtDsRgUubUutUuqUupUuhUusUuo'''))]

    # The following fills the void with nones and returns the list of lists
    mendeleiev = 0

    if mendeleiev:
        for i, j in ((88, 103), (56, 71)):
            L[i] = L[i:j]
            L[i + 1:] = L[j:]
        for i, j in ((12, 10), (4, 10), (1, 16)):
            L[i:i] = [None] * j

        return [L[18 * i:18 * (i + 1)] for i in range(7)]

    # Return a plain list of tuples
    else:
        return L

def Atomn(s, ptable):
    '''Returns the atomic number based on atomic symbol string
    ptable is a list of consecutive (symbol, atomic number) tuples.'''

    for n, a in enumerate(ptable):
        if a[0].lower().find(s.strip().lower()) != -1:
            return float(n + 1)

#----------------------------------------------------------------------------
# Main routine
#----------------------------------------------------------------------------
if __name__ == "__main__":
    Main(sys.argv[1:])
