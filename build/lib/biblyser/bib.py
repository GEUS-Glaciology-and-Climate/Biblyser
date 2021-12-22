"""
The Bib module handles all functionality with a publication, or bib item, such 
as information retrieval from a bib database and authorship analysis
"""

import requests
from datetime import datetime
from habanero import Crossref
from scholarly import scholarly
from biblyser.name import Name, getKeyValue

#------------------------------------------------------------------------------

class Bib(object):
    """The Bib object holds all attributes associated with a publication, 
    such as publication and journal information, citations and altmetrics. 
    Each co-author is linked to the publication as a Name object
    
    Attributes
    ----------
    doi : str
      DOI identification of publication
    title : str
      Publication title
    authors : list
      List of authors (given as Name objects)
    date : datetime
      Date of publication
    ptype : str
      Publication type
    journal : str
      Name of journal published in
    citations : int
      Number of citations
    altmetrics : int
      Altmetric score
    genders : list
      List of author genders
   aff_institutes : list
      List of author institutes
   aff_countries : list
      List of author countries
    """
    
    def __init__(self, **kwargs):
        """Initialise publication object with an inputted variable
        
        Parameters
        ----------           
        **kwargs : dict, optional                  
          Keyword arguments for input to Bib object. Keywords include doi, 
          title, date, ptype, journal, citations, altmetrics and genders
        """
        
        #Take doi and/or title inputs
        if 'doi' in kwargs:
            self.doi = kwargs.get('doi')
            
        if 'title' in kwargs:
            self.title = kwargs.get('title')

        #Check Bib object has doi or title attributes
        if self.doi is None and self.title is None:
            TypeError('Bib object initialisation failed with inputs ' \
                      f'{kwargs}. Expected keywords doi and/or title')
        else:
            
            #Get Name objects if authors are given
            if 'authors' in kwargs:
                author_list = kwargs.get('authors')
                if author_list != None:
                    authors=[]
                    for a in kwargs.get('authors'):
                        authors.append(Name(a))
                    self.authors = authors  
                else:
                    self.authors = None
                
            #Populate other attributes if given
            self.date = getKeyValue(kwargs, 'date')
            self.ptype = getKeyValue(kwargs, 'ptype')
            self.journal = getKeyValue(kwargs, 'journal')
            self.citations = getKeyValue(kwargs, 'citations')
            self.altmetrics = getKeyValue(kwargs, 'altmetrics')
            self.genders = getKeyValue(kwargs, 'genders')
            self.aff_institutes= getKeyValue(kwargs, 'aff_institutes')
            self.aff_countries = getKeyValue(kwargs, 'aff_countries')            
        

    def getFirstAuthor(self):
        """Return first author"""
        return self.authors[0]       

    
    def getLastAuthor(self):
        """Return last author"""
        if len(self.authors) > 1:
            return self.authors[-1]
        else:
            return None


    def getStrAuthors(self):
        """Return all author full names as a comma-delineated string"""
        if self.authors != None:
            all_authors=[]
            for a in self.authors:
                try:
                    all_authors.append(a.originalname)
                except:
                    all_authors.append(a)
            return ', '.join(all_authors)
        else:
            return None
        
        
    def checkBibDate(self, dt):
        """Return if bib was published after a given date
        
        Parameters
        ----------
        dt : datetime
          Given date which bib publication date will be compared to
         
        Returns
        -------
        bool
          Flag denoting if bib was published before (False) or after (True) 
          given date
        """        
        if self.date != None:
            if self.date >= dt:
                return True
        else:
            return False
        
    
    def getOrgAuthors(self, organisation):
        """Return bib authors within organisation
        
        Parameters
        ----------
        organisation : Organisation         
          Organisation object to compare Bib authors to
        
        Returns
        -------
        org_names : list
          List of bib authors that are within Organisation
        """
        org_names=[]
        if self.authors != None:
            for a in self.authors:
                all_a = a.getAllNameFormats()
                for aa in all_a:
                    name = organisation.checkOrgName(aa)
                    if name != None:
                        org_names.append(name)
            org_names = list(set(org_names))
            return org_names
        else:
            return None


    def getOrgGender(self, org_names):
        """Return genders of organisation authors
        
        Parameters
        ----------
        org_names : list
          Name objects within organisation
        
        Returns
        -------
        org_gender : list
          List of organisation author genders
        """
        org_gender=[]
        for on in org_names: 
            org_gender.append(on.getGender())
        return org_gender


    def checkOrgFirstAuthor(self, organisation):
        """Return flag for if first author is within organisation
        
        Parameters
        ----------
        organisation : Organisation       
          Organisation object
        
        Returns
        -------
        out : bool
          Flag denoting if first author is within organisation (True) or 
          external to organisation (False)
        """
        author = self.getFirstAuthor()
        out = False
        for a in author.getAllNameFormats():
            first = organisation.checkOrgName(a)
            if first != None:
                out = True
        return out


    def checkOrgLastAuthor(self, organisation):
        """Return flag for if last author is within organisation
                
        Parameters
        ----------
        organisation :  Organisation    
          Organisation object
        
        Returns
        -------
        out : bool
          Flag denoting if last author is within organisation (True) or 
          external to organisation (False)
        """
        last = self.getLastAuthor()
        if last:
            last_org = organisation.checkOrgName(last)   
        else:
            last_org = None
        return last_org

        
    def retrieveDOIFromTitle(self):
        """Retrieve DOI using a CrossRef search of the Bib title, and append to 
        Bib attributes"""
        if self.title == None:
            print('Publication title not provided. Cannot populate Bib object')
            pass
        else:
            
            #Conduct CrossRef search based on title
            cr = Crossref()   
            clean_title = self.title.lower()
            if '…' in clean_title:
                clean_title = clean_title[:-1]
            search = cr.works(query_title = clean_title, select='title,DOI')
            assert search['status'] == "ok"
            
            #Find matching titles
            info=None
            for item in search['message']['items']:
                fetched = item['title'][0].lower() 
                if fetched == clean_title:
                    info = extractFromCRitem(item)
                    
            #Assign DOI based on search hit
            if info != None:
                self.doi = info[0]
                 
                    
    def retrieveFromAMetric(self): 
        """get Altmetrics of Bib object. If Altmetrics are not already a Bib
        attribute, Altmetrics will be retrieved using a DOI search from the 
        Altmetrics API
        
        Returns
        -------
        int
          Altmetric score
        """
        if self.altmetrics == None:
            try:
                altmet = fetchAltmetrics(self.doi)
                self.altmetrics = getKeyValue(altmet, 'score')
                # getKeyValue(altmet, 'title')
                # getKeyValue(altmet, 'authors')
                # getKeyValue(altmet, 'journal')
                # getKeyValue(altmet, 'type')
                # getKeyValue(altmet, 'published_on')
            except:
                self.altmetrics = None
        return self.altmetrics
            
                            
    def populateBib(self, search):
        """Populate  Bib attributes from search hit
        
        Parameters
        ----------
        search : list
          List of bib information to populate Bib object with [doi, title,
          authors, journal, ptype, date, citations]
        """
        self.doi = search[0]
        self.title = search[1]
        self.authors = search[2]
        self.journal = search[3]
        self.ptype = search[4]
        self.date = search[5]
        self.citations = search[6] 
    
    
#------------------------------------------------------------------------------         

def countGenders(genders):
    """Count genders in list
    
    Parameters
    ----------
    genders : list 
      Gender list to count from
    
    Returns
    -------
    female : int
      Female count
    male : int 
      Male count
    nb : int   
      Non-binary count
    """
    female = genders.count('female')
    male = genders.count('male')
    nb = genders.count('non-binary')
    return female, male, nb


def checkBibAuthors(authors, organisation_names):
    """Check if author name/s appear in organisation names
    
    Parameters
    ----------
    authors : list     
      List of str author names
    organisation_names : list 
      List of str organisation names
    
    Returns
    -------
    check (bool)                            
      Flag denoting if name/s are found
    """
    check=False
    for a in authors:
        if a in organisation_names:
            check=True
    return check


def listToStr(in_list):
    """Return string with comma separation from list
    
    Parameters
    ----------
    in_list : list                          
      List to merge and comma delineate
    
    Returns
    -------
    str or None
      Comma delineated string or None if input is invalid
    """
    if len(in_list) > 1:
        return ', '.join(in_list)
    elif len(in_list) == 1:
        return in_list[0]
    else:
        return None
        

def fromCrossRef(author):
    """Get bib records using CrossRef based on inputted sauthor search
    
    Parameters
    ----------
    author : str
      Author name
    
    Returns
    -------
    out : list
      List containing search hit information [doi, title, authors, journal 
      name, publication type, date, citation count]
    """  
    #Initialise crossref and search
    out=[]
    a = author.lower()
    cr = Crossref()
    
    #Conduct search based on author
    search = cr.works(query=author)
    
    #Match author to names in authorship list
    assert search['status'] == "ok"
    for item in search['message']['items']:
        try:
            for aut in item['author']:
                formatted = aut['given'].lower() + ' ' + aut['family'].lower()
                
                #Retain if match
                if formatted == a:
                    info = extractFromCRitem(item)
                    out.append(info)    
        except:
            pass
    return out


def extractFromCRitem(item):
    """Get bib information from CrossRef search item
    
    Parameters
    ----------
    item : dict
      CrossRef search hit
    
    Returns
    -------
    list
      List containing doi, title, authors, journal name, publication type, 
      date, citation count             
    """ 
    #Get doi
    doi = getKeyValue(item, 'DOI')
    
    #Get journal type and name
    ptype = getKeyValue(item, 'type') 
    journal = getKeyValue(item, 'container-title')
    if journal:
        journal=journal[0]

    #Get publication title
    title = getKeyValue(item, 'title')
    if title:
        title=title[0]
        
    #Get pub date if in valid format
    d = getKeyValue(item, 'created')
    try:
        if d:
            d = d['date-parts'][0]
            date = datetime(d[0], d[1], d[2])
        else:
            date = None
    except:
        date=None
    
    #Get author info if in valid format
    a_obj = getKeyValue(item, 'author')
    if a_obj != None:
        authors=[]
        try:
            [authors.append(a['given']+' '+a['family']) for a in a_obj]
        except:
            authors=None
    else:
        authors=None
                                                
    #Get citation count
    cite = getKeyValue(item, 'is-referenced-by-count')
    
    #Return as list
    return [doi, title, authors, journal, ptype, date, cite]  


def fromScopus(scopus_author):
    """Fetch all publications associated with Scopus author
    
    Parameters
    ----------
    scopus_author : AuthorRetrieval 
      Scopus author retrieval object (scopus.author_retrieval.AuthorRetrieval)
    
    Returns
    -------
    bibs : list
      List of Scopus search publications (scopus.scopus_search.Document)
    """
    bibs = scopus_author.get_documents()   
    return bibs

    
def fromScholar(scholar_author):
    """Fetch all publications associated with Scopus author
    
    Parameters
    ----------
    scholar_author : dict           
      Scholar author dictionary
    
    Returns
    -------
    bibs : list
      List of Scholar bibs
    """
    bibs = []
    
    #Get all publications
    for p in scholar_author['publications']: 
        
        #Populate search hit
        pub = scholarly.fill(p)
    
        #Get info
        doi = extractScholarItem(pub, 'doi')
        title = extractScholarItem(pub, 'title')
        
        authors = extractScholarItem(pub, 'author')
        if authors != None:
            authors = authors.split(' and ')
            
        journal =  extractScholarItem(pub, 'journal') 
        ptype = getKeyValue(pub, 'container_type')
        
        date = extractScholarItem(pub, 'pub_year')
        if date != None:
            date = datetime.strptime(str(date), '%Y')
        
        cite = extractScholarItem(pub, 'num_citations')
        bibs.append([doi, title, authors, journal, ptype, date, cite])
    
    return bibs


def extractScholarItem(pub, item):
    """Extract item from Scholar bib object
    
    Parameters
    ----------
    pub : dict                          
      Scholar bib dictionary
    item : str                          
      Keyword to obtain value from
    
    Returns
    -------
    out : str or int
      Keyword value
    """
    try:
        out = pub['bib'][item]
    except:
        out = None
    return out


def fetchAltmetrics(doi):
    """Fetch altmetrics from DOI
    
    Parameters
    ----------
    doi : str                           
      DOI string to search with
    
    Returns
    -------
    result : dict
      Altmetrics result
    """
    api = 'https://api.altmetric.com/v1/doi/'
    response = requests.get(api + doi)
    if response.status_code == 200:
        result = response.json()
    return result

