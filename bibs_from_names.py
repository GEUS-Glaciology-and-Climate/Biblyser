"""
PyBiblyser (c) is a bibliometric workflow for evaluating the bib metrics of an 
individual or a group of people (an organisation).

PyBiblyser is licensed under a MIT License.

You should have received a copy of the license along with this work. If not, 
see <https://choosealicense.com/licenses/mit/>.
"""

#import pyBibAnalyser classes and functions
from Organisation import Organisation
from BibCollection import BibCollection, orgFromCSV

from bs4 import BeautifulSoup
import requests

# # Set up Scopus configuration (only needs to be done once)
# import pybliometrics
# pybliometrics.scopus.utils.create_config()


#-----------------------   Gather organisation names   ------------------------


def fetchWebInfo(url, parser, fid, classtype, classid):
    '''Get all up-to-date information (e.g. names, titles) from a given webpage
    element id and class'''
    page = requests.get(url)
    soup = BeautifulSoup(page.content, parser)
    results = soup.find(id=fid)
    elements = results.find_all(classtype, class_=classid)
    return elements


#Get names and titles from GEUS Pure webpage
URL = "https://pub.geus.dk/da/organisations/department-of-glaciology-and-climate/persons/"
info = fetchWebInfo(URL, 'html.parser', 'main-content', 'div', 
                    'rendering rendering_person rendering_short rendering_person_short')
names=[]
titles=[]
[names.append(str(e).split('span')[1].split('<')[0].split('>')[1]) for e in info]
[titles.append(str(e).split('span')[5].split('<')[0].split('- ')[1]) for e in info]


# #Get names and titles from GEUS staff webpage
# URL = "https://www.geus.dk/om-geus/kontakt/telefonbog?departmentId=Glaciologi+og+Klima"
# names = fetchWebInfo(URL, 'html.parser', 'gb_ContentPlaceHolderDefault_bottomGrid_ctl03', 
#                     'td', 'contact-name')
# titles = fetchWebInfo(URL, parser, fid, classtype, None)
# titles = info[:][4]


#-------------------------   Create Organisation   ----------------------------


#Define organisation
# org = Organisation(names, titles)                            #All in GEUS G&K
org = Organisation(['Penelope How'])                       #A single person

#Check all authors in organisation
org.checkNames()   

#Populate author info from Scopus and Scholar                         
org.populateOrg()                          

#Export organisation to dataframe
df1 = org.asDataFrame()                     
df1.to_csv('output/out_organisation.csv')  

#------------------------   Create bib database   -----------------------------


#Construct bib object using organisation
bibs = BibCollection(org)                   

#Search for bibs in selected databases (Scopus/Pure, Scholar, CrossRef)
bibs.getScopusBibs()                        
bibs.getScholarBibs()                          
# bibs.getCRBibs()                                                        

#Remove abstracts and discussion papers
bibs.removeAbstracts()                          
bibs.removeDiscussions()  
df_test = bibs.asDataFrame()                      

#Remove duplicates
bibs.removeDuplicates()                         

#Check bibs
bibs.checkBibs()

#Guess genders for all co-authors in BibCollection
gdb = orgFromCSV('output/out_organisation.csv')
bibs.getAllGenders(gdb)

#Export bib database to dataframe           
df2 = bibs.asDataFrame()                   


#--------------------------   Export to file    -------------------------------
    

#Write outputs to csv 
df2.to_csv('output/out_bibs.csv')

gdb_df = gdb.asDataFrame()
gdb_df.to_csv('output/out_database.csv')


#------------------------------------------------------------------------------
print('Finished')