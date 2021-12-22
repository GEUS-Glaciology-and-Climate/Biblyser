"""
Biblyser (c) is a bibliometric workflow for evaluating the bib metrics of an 
individual or a group of people (an organisation).

Biblyser is licensed under a MIT License.

You should have received a copy of the license along with this work. If not, 
see <https://choosealicense.com/licenses/mit/>.
"""

import sys, argparse
sys.path.append('../')
from BibCollection import calcDivIdx

#------------------   Activate parser and parser arguments   ------------------

#Activate parser and parser arguments
parser = argparse.ArgumentParser(description='A script calculate the ' +
                                 ' diversity index of an individual')

parser.add_argument('--name', required=True, type=str, help='Name')

parser.add_argument('--years', default=5, type=int, help='Number of years that' +
                    'diversity index will be determined from')

parser.add_argument('--scopus', default=True, type=bool, 
                    help='Flag denoting whether publications will be ' +
                    'retrieved from Scopus')

parser.add_argument('--scholar', default=False, type=bool, 
                    help='Flag denoting whether publications will be ' +
                    'retrieved from Google Scholar')

parser.add_argument('--crossref', default=False, type=bool, 
                    help='Flag denoting whether publications will be ' +
                    'retrieved from Crossref')

parser.add_argument('--check', default=False, type=bool, help='Flag denoting '+
                    'whether publication search hits should be checked by user')

#Retrieve arguments
args = parser.parse_args()    
name = args.name
years = args.years
scopus = args.scopus
scholar = args.scholar
crossref = args.crossref
check = args.check


calcDivIdx(name, years, scopus, scholar, crossref, check)
