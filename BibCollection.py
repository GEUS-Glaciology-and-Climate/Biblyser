"""
PyBiblyser (c) is a bibliometric workflow for evaluating the bib metrics of an 
individual or a group of people (an organisation).

PyBiblyser is licensed under a MIT License.

You should have received a copy of the license along with this work. If not, 
see <https://choosealicense.com/licenses/mit/>.
"""

import numpy as np
import pandas as pd
from datetime import datetime
from scholarly import scholarly
import gender_guesser.detector as gender
from pybliometrics.scopus import AuthorRetrieval

from Name import Name, guessGender, defineGender
from Bib import Bib, fromCrossRef, fromScholar, fromScopus, countGenders, \
    listToStr
from Organisation import Organisation, orgFromCSV, checkGender

#------------------------------------------------------------------------------

class BibCollection(object):
    """A collection of Bib objects, representing a database of publications
    
    Attributes
    ----------
    organisation : Organisation
      Organisation object associated with BibCollection
    bibs : list
      List of Bib objects
    """
    
    def __init__(self, args):
        """Initialise BibCollection object
        
        Parameters
        ----------
        args : Organisation or list
          An Organisation object or list of Bib or Name objects
        """
        print(f'Defining BibCollection object from {type(args)}...')
        
        #Assign from Organisation object input
        if isinstance(args, Organisation):
            self.organisation = args
            self.bibs = None
            
        #Assign from Bib objects or doi list
        elif isinstance(args, list):
            
            #Compile Bib objects
            if isinstance(args[0], Bib):
                self.organisation = None
                self.bibs = args
            
            #Retrieve Bib objects from DOI strings
            elif isinstance(args[0], Name):
                self.organisation = Organisation(args)
                self.bibs = None
                
        #Create organisation from Name objects or strings input
        else:
            raise TypeError(f'Invalid input {args}, type {type(args)}')


    def getOrganisation(self):
        """Return Organisation object
        
        Returns
        -------
        Organisation
          Organisation object affiliated with BibCollection object
        """
        return self.organisation
    
        
    def addOrganisation(self, org):
        '''Add affiliated Organisation object to BibCollection
        
        Parameters
        ----------
        org : Organisation
          Organisation to add to object
        '''
        self.organisation = org
        
        
    def addBibs(self, bibs_list):
        """Add list of Bib objects to BibCollection object
        
        bibs_list : list
          List of Bib objects to add to BibCollection object
        """
        if self.bibs != None:
            [self.bibs.append(b) for b in bibs_list]   
        else:
            self.bibs = bibs_list  
        
        
    def getCRBibs(self):
        """Retrieve CrossRef bibs associated with authors in organisation"""
        bibs=[]
        org = self.getOrganisation()
        for n in org.names:  
             
             #Get all name formats of author
             all_formats = n.getAllNameFormats()
             
             #Retrieve publications from CrossRef 
             for f in all_formats:
                 search1 = fromCrossRef(author=f)
                                  
                 #Construct Bib oject from all search hits
                 for s in search1:
                     bibs.append(Bib(doi=s[0], title=s[1], authors=s[2],
                                     journal=s[3], ptype=s[4], date=s[5],
                                     citations=s[6]))       
        #Append Bib objects
        self.addBibs(bibs)                    


    def getScopusBibs(self):        
        """Retrieve all Scopus bibs associated with authors in organisation"""
        bibs=[]
        org = self.getOrganisation()
        for n in org.names: 
            
            #Retrieve Scopus ID author and all publications
            if n.scopusid != None:
                author = AuthorRetrieval(n.scopusid)   
                scopus_bibs = fromScopus(author) 
                
                #Extract information from all scopus bibs
                for s in scopus_bibs:                
                    a = []
                    a_split = s.author_names.split(';')
                    for asp in a_split:
                        a.append(' '.join([asp.split(', ')[1],asp.split(', ')[0]]))
                    d = datetime.strptime(str(s.coverDate), '%Y-%m-%d')
                    
                    #Construct Bib object
                    bibs.append(Bib(doi=s.doi, 
                                    title=s.title, 
                                    authors=a,
                                    journal=s.publicationName, 
                                    ptype=s.aggregationType, 
                                    date=d,
                                    citations=s.citedby_count))                       
        #Append Bib objects
        self.addBibs(bibs) 
       

    def getScholarBibs(self):
        """Retrieve all Scholar bibs associated with authors in organisation"""
        bibs=[]
        org = self.getOrganisation()
        
        #Iterate through organisation Name objects
        for n in org.names:  
            
            #Check for Google Scholar ID 
             if n.scholarid != None:
                 
                 #Fetch bibs using ID search
                 author = scholarly.search_author_id(n.scholarid)
                 author = scholarly.fill(author)
                 search = fromScholar(author)
                            
                 #Compile search hits into bib objects
                 for s in search:
                     b = Bib(doi=s[0], title=s[1], authors=s[2], journal=s[3], 
                             ptype=s[4], date=s[5], citations=s[6]) 
                     
                     #Retrieve DOI if not given in Scholar hit
                     if b.doi == None:
                         b.retrieveDOIFromTitle()
                     bibs.append(b)
                     
        #Append Bib objects
        self.addBibs(bibs) 
        
         
    def removeBib(self, idx):
        """Remove bib from BibCollection based on index position
        
        Parameters
        ----------
        idx : int                       
          Index position of bib to delete
        """
        del self.bibs[idx]  


    def removeFromKeyword(self, bib_att, keyword):
        """Remove bibs from BibCollection based on keyword (case non-specific) 
        in specified bib attribute journal
        
        Parameters
        ----------
        bib_att : list
          Bib attribute list to base removal on
        keyword : str
          Word to classify removal
        """
        idx=[]
        
        #Check if keyword is in bib attribute
        for b in range(len(bib_att)):
            try:
                journal = bib_att[b].lower()
                if keyword in journal:
                    idx.append(b)
            except:
                pass
        
        #Delete all bibs based on retained indices
        if idx != None:
            idx.reverse()
            [self.removeBib(i) for i in idx]
            

    def removeAbstracts(self):
        """Remove conference abstract bibs from BibCollection based on journal
        title containinng the word "abstract" (case non-specific)"""
        journals = []
        [journals.append(b.journal) for b in self.bibs]
        self.removeFromKeyword(journals, 'abstract')


    def removeDiscussions(self):
        """Remove discussion paper bibs from BibCollection based on journal
        title containinng the word "discussion" (case non-specific)"""
        journals = []
        [journals.append(b.journal) for b in self.bibs]
        self.removeFromKeyword(journals, 'discussion')
                

    def checkBibs(self): 
        """Checker for Bibs in BibCollection"""
        #Begin loop
        r1='y'
        while True:
            
            #Show revised Bibcollection
            df = self.asDataFrame()
            pd.set_option('display.max_rows', None)
            print(df['title'])
            
            #User prompted removal proceed if 'n'
            r1 = input ('Do any bibs need removing? [y/n] ')
            if r1 in ['y']:
                
                #Identify bib object to remove
                r2 = input (f'Which bib needs removing? [0-{len(df.index)-1}] ')
                if 0 <= int(r2) <= len(df.index):
                    a = self.bibs[int(r2)]
                    authors = a.getStrAuthors()
                    print(f'\nBib {r2} \nDOI {a.doi}' \
                          f'\nTitle: {a.title} \nJournal: {a.journal}' \
                          f'\nAuthors: {authors} \n Date: {a.date}' )
                    r3 = input('Are you sure you want to delete this one? [y/n] ')
                    if r3 in ['y']:
                        self.removeBib(int(r2))
                    elif r3 in ['n']:
                        pass
           
            #Exit if 'n'
            elif r1 in ['n']: 
                break
            
            
    def removeDuplicates(self):
        """Remove duplicate bib objects from BibCollection based on doi and 
        title"""
        #Get dois and find duplicates
        dois = []
        [dois.append(str(b.doi).lower()) for b in self.bibs]
        i1 = findDuplicates(dois)
        
        #Get titles and find duplicates
        titles= [] 
        [titles.append(str(b.title).lower()) for b in self.bibs]
        i2 = findDuplicates(titles)
        
        #Merge indices and remove bibs
        idx = list(set(np.concatenate((i1, i2)).tolist()))                
        if idx != None:
            idx.reverse()
            [self.removeBib(i) for i in idx]
            

    def getRecent(self, dt):
        """Return all bibs in BibCollection that were published after a certain
        date (given as a datetime object)
        
        Parameters
        ----------
        dt : datetime
          Datetime to filter bibs 
        
        Returns
        -------
        new_bibs : BibCollection       
          BibCollection with only recent Bibs
        """
        recent_bibs = []
        
        #Check date of each bib
        for bib in self.bibs:
            check = bib.checkBibDate(dt)
            if check:
                recent_bibs.append(bib)
                
        #Add bibs to new Bib Collection object
        try:
            new_bibs = BibCollection(self.organisation) 
            new_bibs.addBibs(recent_bibs)
        except:
            new_bibs = BibCollection(recent_bibs)
        return new_bibs
        
        
    def getAllGenders(self, database):
        """Fetch genders of all co-authors in BibCollection, using database
        to retain user defined co-author genders
        
        Parameters
        -----------
        database : Organisation or str
          Database of names and genders, either as an Organisation object or as
          a .csv filepath to an Organisation dataframe
        """
        if isinstance(database, Organisation):
            gdb = database
        elif isinstance(database, str):
            gdb = orgFromCSV(database)
        else:
            TypeError(f'Got database type {type(database)}. ' \
                      'Expecting type Organisation or str')
        
        #Iterate through Bibs in BibCollection
        for b in self.bibs:
            gens = []
            for author in b.authors:
        
                #Check name in database
                g = checkGender(author.fullname, gdb)
               
                #Guess gender
                if not g:            
                    guesser = gender.Detector()
                    g = guessGender(guesser, author.fullname)
                
                    #If name is ambiguous, define gender manually
                    if g in ['unknown', 'andy', 'mostly_male', 'mostly_female']:
                        g = defineGender(author.fullname)
                        
                    #Add name to database
                    author.gender = g             
                    gdb.addName(author)
                      
            #Append author genders     
                gens.append(g)        
            b.genders = gens 
                
        
    def asDataFrame(self):
        """Retrieve BibCollection attributes as dataframe
        
        Returns
        -------
        df : pandas.DataFrame
          Dataframe containing all attributes of BibCollection object
        """
        df = pd.DataFrame()
        for b in self.bibs:
            
            #Get formatted authors
            if b.authors != None:
                author_str = b.getStrAuthors()
                
                #Get organisation affiliated authors            
                oa = b.getOrgAuthors(self.organisation)
                org_authors = []
                [org_authors.append(author.fullname) for author in oa]
                org_authors = listToStr(org_authors)
                org_first = str(b.checkOrgFirstAuthor(self.organisation))
            else:
                author_str = None
                org_authors = None
                org_first = None
          
            #Get authors genders
            genders = b.genders
            if genders != None:
                first = genders[0]
                if len(genders) > 1:
                    last = genders[-1]
                    genders_str = ', '.join(genders)
                else:
                    last = None
                    genders_str = genders[0]    
                f, m, nb = countGenders(genders)
            else:
                genders_str=None
                first=None
                last=None
                f=None
                m=None
                nb=None
            
            #Construct pandas series and append to dataframe
            series = pd.Series({'doi': b.doi, 
                              'title': b.title,
                              'type': b.ptype, 
                              'journal': b.journal,
                              'date': b.date, 
                              'citations': b.citations,
                              'altmetric': b.retrieveFromAMetric(),
                              'authors': author_str, 
                              'org_led': org_first,
                              'org_authors': org_authors,
                              'genders': genders_str,
                              'first_gender': first,
                              'last_gender': last,
                              'female_authors': f,
                              'male_authors': m,
                              'nonbinary_authors': nb})
            df = df.append(series, ignore_index=True)
        return df
    
#------------------------------------------------------------------------------
 
def findDuplicates(l):
    """Find index of duplicates in list, disregarding nan values
    
    Parameters
    ----------
    l : list
      List to find duplicates in
    
    Returns
    -------
    idx : list
      List of duplicate indices
    """
    df = pd.DataFrame(l)
    df = df.replace(to_replace='none', value=np.nan)
    df = df.dropna().loc[df[0].duplicated(keep='first')]
    idx = df.index
    return idx