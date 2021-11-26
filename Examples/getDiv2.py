"""
PyBiblyser (c) is a bibliometric workflow for evaluating the bib metrics of an 
individual or a group of people (an organisation).

PyBiblyser is licensed under a MIT License.

You should have received a copy of the license along with this work. If not, 
see <https://choosealicense.com/licenses/mit/>.
"""
from datetime import datetime, timedelta
import pybliometrics, copy, sys

sys.path.append('../')
from Bib import countGenders
from Organisation import Organisation
from BibCollection import BibCollection

# # Set up Scopus configuration (only needs to be done once)
# import pybliometrics
# pybliometrics.scopus.utils.create_config()

#-----------------------------   Set inputs  ----------------------------------
  
name = 'Penelope How'
years = 5

scopus = False
scholar = True
crossref = False

check = True

#----------------------   Create Name to search from   ------------------------

#Define organisation
n = Organisation([name])

#Check all authors in organisation
if check:
    n.checkNames()   

#Populate author info from Scopus and Scholar                         
n.populateOrg()                          

#------------------------   Create bib database   -----------------------------

#Construct bib object using organisation
bibs = BibCollection(n)                   

#Search for bibs in selected databases
if scopus:
    bibs.getScopusBibs()                       #From Scopus (Pure)
if scholar:
    bibs.getScholarBibs()                      #From Google Scholar
if crossref:
    bibs.getCRBibs()                           #From CrossRef

#Filter gathered bibs
bibs.removeAbstracts()                          #Remove abstracts
bibs.removeDiscussions()                        #Remove discussion papers
bibs.removeDuplicates()                         #Remove duplicate search hits
                  
#---------------------------   Extract bibs   ---------------------------------

#Calculate time range for bib search
now = datetime.now()
past = now - timedelta(days=years*365)
nowstr = now.strftime("%d/%m/%Y")
paststr = past.strftime("%d/%m/%Y")
print(f'Extracting publications from {paststr} to {nowstr}')

#Retrieve bibs within time range         
new = bibs.getRecent(past)  

#Remove bibs with 1 author or >20 authors
idx=[]
for i in range(len(new.bibs)):
    if new.bibs[i].authors != None:
        if len(new.bibs[i].authors) == 1 or len(new.bibs[i].authors) > 20:
            idx.append(i)
if idx != None:
    idx.reverse()
    [new.removeBib(i) for i in idx]

#------------------------   Create gender stats   -----------------------------

#Check bibs
if check:
    new.checkBibs()

#Guess genders for all co-authors in BibCollection
gdb = copy.copy(n)
new.getAllGenders(gdb) 

#----------------------   Calculate div index   -------------------------------

#Get list of genders for each bib
genders=[]
[genders.append(b.genders) for b in new.bibs] 

#Count genders
div = []
for g in genders:
    f,m,nb = countGenders(g)
    
    #Make ratio of female and non-binary authors to total number of authors
    ratio = (f+nb) / len(g)
    div.append(ratio)

#Find average, max and min of all bib authorship ratios
max_div = max(div)
min_div = min(div)
ave_div = sum(div) / len(div)      

print('\n\nYour diversity index is %.1f [0-1]' % ave_div)
print('Your maximum diversity index is %.1f' % max_div)
print('Your minimum diversity index is %.1f' % min_div)
print(f'Your diversity index is based on {len(div)} publications ' \
      f'between {paststr} and {nowstr}, where 0 denotes a total male ' \
      f'authorship, 1 denotes total non-male authorship, and 0.5 is a balance')