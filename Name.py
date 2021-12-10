"""
The Name module handles all functionality with an author name, including 
formatting, gender, and affiliated bib information
"""

import numpy as np
from scholarly import scholarly
import gender_guesser.detector as gender
from pybliometrics.scopus import AuthorSearch, AuthorRetrieval
    
#------------------------------------------------------------------------------

class Name(object):
    """The Name object holds all information related to an author of a 
    publication, such as full name, title, gender, affiliation, and 
    identifications for bib databases such as Scopus and Google Scholar
    
    Attributes
    ----------
    fullname : str
      Full name
    firstname : str
      First name
    middlename : str
      Middle name
    surname : str
      Last name
    originalname : str
      Original inputted name to object
    title : str
      Title associated with name (e.g. researcher, technician)
    gender : str
      Gender associated with name (female, male, or non-binary)
    orcid : str
      ORCID identification 
    hindex_scopus : int
      H-index from Scopus
    hindex_scholar : int
      H-index from Scholar
    scopusid : str
      Scopus author identification
    scholarid : str
      Scholar author idenitification
    affiliation : str
      Affiliation institute or university
    """
    
    def __init__(self, name, title=None, gender=None, **kwargs):
        """Initialise name object
        
        Parameters
        ----------
        name : str                  
          Author name, either given as full name string (e.g. "Jane Emily Doe") 
          or as list containing first and surname (e.g. ["Jane","Doe"] or 
          first, middle and surname (e.g. ["Jane", "Emily", "Doe"])
        title : str, optional                 
          Title of author, such as "Researcher" or "Technician"
        gender : str, optional                
          Gender of author
        **kwargs : dict, optional                   
          Keyword arguments for Name attributes (valid keywords: orcid, 
          scholarid, scopusid, hindex_scopus, hindex_scholar, affiliation)
        """
        #If fullname is provided
        if isinstance(name, str):
            self.fullname = name
            self.firstname, self.middlename, self.surname = splitFullName(name)
        
        #If first and surname provided as list
        elif isinstance(name, list): 
            if len(name)==2:
                self.firstname = name[0]
                self.surname = name[1]
                self.middlename = None
                self.fullname = name[0] + ' ' + name[1]
            
            #If first, middle and surname provided as list
            elif len(name)>2:
                self.firstname = name[0]
                self.middlename = name[1]
                self.surname = name[2]
                self.fullname = name[0] + ' ' + name[1] + ' ' + name[2]
            
            else:
                raise ValueError(f'Input {name} list not valid')
        
        #Else, raise error
        else:
            raise TypeError(f'Input {name} not valid')
        
        #Retain original name input
        self.originalname = name
        
        #Assign title and gender attributes from input
        self.title = title
        self.gender = gender
        
        #Create other attributes from kwargs       
        self.orcid = getKeyValue(kwargs, 'orcid')
        self.hindex_scopus = getKeyValue(kwargs, 'hindex_scopus')
        self.hindex_scholar = getKeyValue(kwargs, 'hindex_scholar') 
        self.scopusid = getKeyValue(kwargs, 'scopusid')
        self.scholarid = getKeyValue(kwargs, 'scholarid')
        # self.affiliation = getKeyValue(kwargs, 'affiliation')
        # self.country = getKeyValue(kwargs, 'country')
  
    
    def populateFromScopus(self):
        """Populate Name attributes using Scopus AuthorSearch"""
        author = fetchScopusAuthor(self.firstname, self.surname)
        try:
            self.orcid = author.orcid
        except:
            pass
        try:
            self.hindex_scopus = author.h_index
        except:
            pass
        try:
            self.scopusid = author.eid
        except:
            pass
        # try:
        #     self.affiliation = author.affiliation_current[0].preferred_name

        # except:
        #     pass
        # try:
        #     self.country = author.affiliation_current[0].country            
        # except:
        #     pass
        
    def populateFromScholar(self):
        """Populate Name attributes using Scholar search"""
        author = fetchScholarAuthor(self.firstname, self.surname)
        if author != None:
            hindex = getKeyValue(author, 'hindex')
            if hindex != None:
                self.hindex_scholar = float(hindex)
            else:
                self.hindex_scholar = np.nan   
            self.scholarid = getKeyValue(author, 'scholar_id')
            # self.affiliation = getKeyValue(author, 'affiliation')
        
        
    def getGender(self):
        """Return gender attribute. If not given, guess gender based on first 
        name
        
        Returns
        -------
        str
          Gender attribute of object
        """
        if self.gender is None:
            
            #Guess gender from first name
            guesser = gender.Detector()
            g = guessGender(guesser, self.fullname)
            
            #If name is ambiguous, define gender manually
            if g in ['unknown', 'andy', 'mostly_male', 'mostly_female']:
                g = defineGender(self.fullname)
            
            #Assign gender to attributes
            self.gender = g
        return self.gender      
    
    
    def getTitle(self):
        """Return title associated with name
        
        Returns
        -------
        str 
          Title attribute of object
        """
        if self.title == None:
            while True:
                title = input(f'Please provide title for {self.fullname}: ')
                if title != None:
                    break
            self.title = title
        else:
            return self.title
    
    
    def getFullInitials(self):
        """Get name with all initials formatting e.g. "Jane Emily Doe" >> 
        "J. E. Doe" 
        
        Returns
        -------
        str
          Full initials version of name
        """
        if self.middlename is not None:
            parts = self.middlename.split(' ')
            mid = ''
            for p in parts:
                mid+= getInitial(p)
            return getInitial(self.firstname) + mid + self.surname
        else:
            return self.getSingleInitials()
        
    
    def getSingleInitials(self):     
        """Get name with single initials formatting e.g. "Jane Emily Doe" >> 
        "J. Doe" 
        
        Returns
        -------
        str
          Single initials version of name
        """       
        return getInitial(self.firstname) + self.surname   


    def getSingleName(self):
        """Get name with single first name formatting e.g. "Jane Emily Doe" >>
        "Jane Doe"
        
        Returns
        -------
        str
          Single firt name version of name
        """
        return self.firstname + ' ' + self.surname


    def getNameAndInitials(self):   
        """Get full first name and initialled middle names formatting e.g.
        "Jane Emily Doe" >> "Jane E. Doe"
        
        Returns
        -------
        str
          First name and initials version of name
        """
        if self.middlename is not None:
            parts = self.middlename.split(' ')
            mid = ''
            for p in parts:
                mid+= getInitial(p)
            return self.firstname + ' ' + mid + self.surname
        else:
            return self.getSingleName()

    
    def getAllNameFormats(self):
        """Return all name formats - fullname, all initials, single initials,
        and name and middle name initials
                
        Returns
        -------
        list
          All versions of name [full name, all initials, single initials, 
          first name and initials]
        """
        return [self.fullname, self.getFullInitials(), 
                 self.getSingleInitials(), self.getNameAndInitials()]
    
    
    def matchName(self, n):
        """Check if name matches formatted names, with a boolean output
        
        Parameters
        ----------
        n : str
          Name to match with
        
        Returns
        -------
        bool
          Flag denoting whether name matches (True) or not (False)
        """
        all_formats = self.getAllNameFormats()
        if n in all_formats:
            return True
        else:
            return False
       
#------------------------------------------------------------------------------    

def getKeyValue(kwarg, key):
    """Return key value from dictionary if present
    
    Parameters
    ----------
    kwarg : dict                      
      Dict object to find key from
    key : str 
      Key to retrieve value from
      
    Returns
    -------
    str or int or None
      Keyword value, None if key is invalid
    """
    if key in kwarg:
        return kwarg.get(key)
    else:
        return None 
 
    
def getInitial(name):
    """Get initial from name e.g. "Jane" >> "J. " 
    
    Parameters
    ----------
    name :str                          
      Name to retrieve initial from
      
    Returns
    -------
    str
      Initialised name
    """
    return name[0] + '. '


def splitFullName(fullname):
    """Split full name into first, middle and last name e.g. "Jane Emily Doe" 
    >> ["Jane", "Emily", "Doe"]
    
    Parameters
    ----------
    fullname : str
      Full name string
    
    Returns
    -------
    first : str
      First name string
    middle : str
      Middle name string
    last : str
      Last name string
    """   
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
    """Guess gender from name using the gender_guesser package
    
    Parameters
    ----------
    guesser : detector.Detector
      Gender guesser object
    fullname : str
      Full name
    
    Returns
    -------
    gname : str
      Guessed gender of name
    """  
    name = fullname.split(' ')[0]
    gname = guesser.get_gender(name, country)
    return gname
    

def defineGender(fullname): 
    """User-define gender of fullname with prompted input
    
    Parameters
    ----------
    fullname : str
      Full name  
    
    Returns
    -------
    gname : str
      "male"/"female"/"non-binary"
    """
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
    """Fetch Scopus author object using name search with Scopus API
    
    Parameters
    ----------
    firstname : str                      
      First (and middle) name string
    lastname : str
      Last name string
    
    Returns
    scopus_author : AuthorRetrieval
      Scopus author retrieval object (scopus.author_retrieval.AuthorRetrieval)
    """
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
    """Fetch Scholar author object using name search with Google Scholar API
    
    Parameters
    ----------
    firstname : str                      
      First (and middle) name string
    lastname : str
      Last name string
    
    Returns
    -------
    scholar_author : dict
      Google Scholar author attributes    
    """  
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
               