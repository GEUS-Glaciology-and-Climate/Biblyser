"""
PyBiblyser (c) is a bibliometric workflow for evaluating the bib metrics of an 
individual or a group of people (an organisation).

PyBiblyser is licensed under a MIT License.

You should have received a copy of the license along with this work. If not, 
see <https://choosealicense.com/licenses/mit/>.
"""

import numpy as np
from scholarly import scholarly
import gender_guesser.detector as gender
from pybliometrics.scopus import AuthorSearch, AuthorRetrieval
    
#------------------------------------------------------------------------------

class Name(object):
    '''The Name object holds all information related to an author of a 
    publication, such as full name, title, gender, affiliation, and 
    identifications for bib databases such as Scopus and Google Scholar'''
    
    def __init__(self, name, title=None, gender=None, **kwargs):
        '''Initialise name object
        
        Variables
        name (str)                  Author name, either given as full name 
                                    string (e.g. "Jane Emily Doe") or as list 
                                    containing first and surname (e.g. 
                                    ["Jane","Doe"] or first, middle and 
                                    surname (e.g. ["Jane", "Emily", "Doe"])
        title (str)                 Title of author, such as "Researcher" or
                                    "Technician" (default=None)
        gender (str)                Gender of author (default=None)
        **kwargs                    Keyword arguments for Name attributes
                                    (valid keywords: orcid, scholarid, 
                                    scopusid, hindex_scopus, hindex_scholar,
                                    affiliation)
        '''
        #If fullname is provided
        if isinstance(name, str):
            self._fullname = name
            self._firstname, self._middlename, self._surname = splitFullName(name)
        
        #If first and surname provided as list
        elif isinstance(name, list): 
            if len(name)==2:
                self._firstname = name[0]
                self._surname = name[1]
                self._middlename = None
                self._fullname = name[0] + ' ' + name[1]
            
            #If first, middle and surname provided as list
            elif len(name)>2:
                self._firstname = name[0]
                self._middlename = name[1]
                self._surname = name[2]
                self._fullname = name[0] + ' ' + name[1] + ' ' + name[2]
            
            else:
                raise ValueError(f'Input {name} list not valid')
        
        #Else, raise error
        else:
            raise TypeError(f'Input {name} not valid')
        
        #Retain original name input
        self._originalname = name
        
        #Assign title and gender attributes from input
        self._title = title
        self._gender = gender
        
        #Create other attributes from kwargs       
        self._orcid = getKeyValue(kwargs, 'orcid')
        self._hindex_scopus = getKeyValue(kwargs, 'hindex_scopus')
        self._hindex_scholar = getKeyValue(kwargs, 'hindex_scholar') 
        self._scopusid = getKeyValue(kwargs, 'scopusid')
        self._scholarid = getKeyValue(kwargs, 'scholarid')
        self._affiliation = getKeyValue(kwargs, 'affiliation')
  
    
    def populateFromScopus(self):
        '''Populate Name attributes using Scopus AuthorSearch'''
        author = fetchScopusAuthor(self._firstname, self._surname)
        try:
            self._orcid = author.orcid
        except:
            pass
        try:
            self._hindex_scopus = author.h_index
        except:
            pass
        try:
            self._scopusid = author.eid
        except:
            pass
        try:
            self._affiliation = author.affiliation_current
        except:
            pass
            

    def populateFromScholar(self):
        '''Populate Name attributes using Scholar search'''
        author = fetchScholarAuthor(self._firstname, self._surname)
        if author != None:
            hindex = getKeyValue(author, 'hindex')
            if hindex != None:
                self._hindex_scholar = float(hindex)
            else:
                self._hindex_scholar = np.nan
                
            self._scholarid = getKeyValue(author, 'scholar_id')
            self._affiliation = getKeyValue(author, 'affiliation')
        
        
    def getGender(self):
        '''Guess gender based on first name'''
        if self._gender is None:
            
            #Guess gender from first name
            guesser = gender.Detector()
            g = guessGender(guesser, self._fullname)
            
            #If name is ambiguous, define gender manually
            if g in ['unknown', 'andy', 'mostly_male', 'mostly_female']:
                g = defineGender(self._fullname)
            
            #Assign gender to attributes
            self._gender = g
        return self._gender      
    
    
    def getTitle(self):
        '''Return title associated with name'''
        if self._title == None:
            while True:
                title = input(f'Please provide title for {self._fullname}: ')
                if title != None:
                    break
            self._title = title
        else:
            return self._title
    
    
    def getFullInitials(self):
        '''Get name with all initials formatting e.g. "Jane Emily Doe" >> 
        "J. E. Doe" '''
        if self._middlename is not None:
            parts = self._middlename.split(' ')
            mid = ''
            for p in parts:
                mid+= getInitial(p)
            return getInitial(self._firstname) + mid + self._surname
        else:
            return self.getSingleInitials()
        
    
    def getSingleInitials(self):     
        '''Get name with single initials formatting e.g. "Jane Emily Doe" >> 
        "J. Doe" '''        
        return getInitial(self._firstname) + self._surname   


    def getSingleName(self):
        '''Get name with single first name formatting e.g. "Jane Emily Doe" >>
        "Jane Doe" '''
        return self._firstname + ' ' + self._surname


    def getNameAndInitials(self):   
        '''Get full first name and initialled middle names formatting e.g.
        "Jane Emily Doe" >> "Jane E. Doe" '''
        if self._middlename is not None:
            parts = self._middlename.split(' ')
            mid = ''
            for p in parts:
                mid+= getInitial(p)
            return self._firstname + ' ' + mid + self._surname
        else:
            return self.getSingleName()

    
    def getAllNameFormats(self):
        '''Return all name formats - fullname, all initials, single initials,
        and name and middle name initials'''
        return [self._fullname, self.getFullInitials(), 
                 self.getSingleInitials(), self.getNameAndInitials()]
    
    
    def matchName(self, n):
        '''Check if name matches formatted names, with a boolean output
        
        Variables
        n (str)                     Name to match with
        '''
        all_formats = self.getAllNameFormats()
        if n in all_formats:
            return True
        else:
            return False
       
#------------------------------------------------------------------------------    

def getKeyValue(kwarg, key):
    '''Return key value from kwarg key if present
    
    Variables
    kwarg (dict)                        Dict object to find key from
    key (str)                           Key to retrieve value from
    '''
    if key in kwarg:
        return kwarg.get(key)
    else:
        return None 
 
    
def getInitial(name):
    '''Get initial from name e.g. "Jane" >> "J. " 
    Variables
    name (str)                          Name to retrieve initial from'''
    return name[0] + '. '


def splitFullName(fullname):
    '''Split full name into first, middle and last name e.g. "Jane Emily Doe" 
    >> ["Jane", "Emily", "Doe"]
    
    Variables
    fullname (str)                      Full name string
    
    Return
    first (str)                         First name string
    middle (str)                        Middle name string
    last (str)                          Last name string
    '''     
    parts = fullname.split(' ')
    
    #If only first and surname
    if len(parts)==2:
        first = parts[0]
        last = parts[1]
        middle=None
    
    #If first, middle and surname
    elif len(parts)>2:
        first = parts[0]
        last = parts[-1]
        
        #If one middle name
        if len(parts)==3:
            middle = parts[1]
        
        #If more than one middle name
        else:
            middle=''
            for p in parts[1:-2]:
                middle += p + ' '
            middle += parts[-2]
    elif len(parts)==1:
        first=None
        last=parts[0]
        middle=None
    return first, middle, last
        

def guessGender(guesser, fullname, country=None):
    '''Guess gender from name using the gender_guesser package
    
    Variables
    guesser (detector.Detector)             Gender guesser object
    fullname (str)                          Full name
    
    Return
    gname (str)                             Gender of name
    '''   
    name = fullname.split(' ')[0]
    gname = guesser.get_gender(name, country)
    return gname
    

def defineGender(fullname): 
    '''User-define gender of fullname with prompted input
    
    Variables 
    fullname (str)                          Full name  
    
    Return 
    gname (str)                             "male"/"female"/"non-binary
    '''
    #User input for gender
    while True:
        usr = input (f'Is {fullname} male, female or non-binary [m/f/nb]? ')
        if usr in ['m', 'f', 'nb']:
            break
        
    #Assign gender from letter
    if usr == 'm': 
        gname='male'
    elif usr == 'f': 
        gname='female'
    elif usr == 'nb':
        gname='non-binary'              
    return gname


def fetchScopusAuthor(firstname, lastname):
    '''Fetch Scopus author object using name search with Scopus API
    
    Variables 
    name (str)                      Fullname string
    
    Returns
    scopus_author (AuthorRetrieval) Scopus author retrieval object
                                    (scopus.author_retrieval.AuthorRetrieval)
    '''
    #Search for authors based on name
    try:
        a_search = AuthorSearch(f'AUTHLAST({lastname}) and AUTHFIRST({firstname})')
    except:
        print(f'Scopus information for {firstname} {lastname} not retrieved')
        return None

     #Retain first hit if one search result found
    if a_search.get_results_size() == 0:
        idx = None
    elif a_search.get_results_size() == 1:
        idx = 0

    #User input prompt if more than author found
    else:
        print('Multiple authors found in search:')
        print(a_search)
        size = a_search.get_results_size()
        while True:
            i = input(f'Which author is correct? [1-{size}, or press enter to skip] ')
            if i == '':
                idx = None
                break
            else:
                if int(i) in range(a_search.get_results_size()+1):
                    idx = int(i)-1
                    break

    #Retrieve author from AuthorSearch object
    if idx != None:
        scopus_author = AuthorRetrieval(a_search.authors[idx].eid)
        return scopus_author
    else:
        print(f'Scopus information for {firstname} {lastname} not retrieved')
        return None


def fetchScholarAuthor(firstname, lastname):
    '''Fetch Scholar author object using name search with Google Scholar API
    
    Variables 
    name (str)                      Fullname string
    
    Returns
    scholar_author (dict)           Google Scholar author attributes    
    '''    
    #Retrieve the author's data, fill-in, and print
    fullname = ' '.join([firstname, lastname])
    search_query = scholarly.search_author(fullname)  
    
    #Fill search hit
    try:
        scholar_author = scholarly.fill(next(search_query))
    except:
        print(f'Google Scholar information for {fullname} not retrieved')
        scholar_author = None
    
    #Close query
    search_query.close()
    return scholar_author

                  