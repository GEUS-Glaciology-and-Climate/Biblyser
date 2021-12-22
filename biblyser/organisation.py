"""
The Organisation module handles all functionality with a collection of author 
names
"""

import pandas as pd
from biblyser.name import Name, getKeyValue

#------------------------------------------------------------------------------    

class Organisation(object):
    """The Organisation object holds a collection of Name objects, 
    representing an institution or department

    Attributes
    ----------    
    names : list
      List of Name objects
    """
    def __init__(self, names, titles=None, genders=None, **kwargs):
        """Initialise organisation from list of names
        
        Parameters
        ----------
        names : list or str               
          List of str names or Name objects
        titles : list, optional
          List of str titles
        genders : list, optional
          List of str genders
        **kwargs : dict
          Keyword arguments (valid keywords: orcid, cholarid, scopusid, 
          hindex_scopus, hindex_scholar, affiliation)        
        """
        print(f'Constructing Organisation from {type(names)}')
        if isinstance(names, list): 
            
            #Construction from list of Name objects
            if isinstance(names[0], Name):
                self.names = names
                
            #Construction from list containing name strings                
            elif isinstance(names[0], str) or isinstance(names[0], list): 
                new=[]
                for i in range(len(names)):
                    new_name = Name(names[i])
                    if titles != None:
                        new_name.title = titles[i]
                    if genders != None:
                        new_name.gender = genders[i]
                        
                    try:
                        new_name.orcid = getKeyValue(kwargs, 'orcid')[i]
                        new_name.scopusid = getKeyValue(kwargs, 'scopusid')[i]
                        new_name.hindex_scopus = getKeyValue(kwargs, 
                                                              'hindex_scopus')[i]
                        new_name.hindex_scholar = getKeyValue(kwargs, 
                                                               'hindex_scholar')[i]
                    except:
                        self.orcid = None
                        self.scopusid = None
                        self.hindex_scopus = None
                        self.hindex_scholar = None
                    new.append(new_name)
                    
                self.names = new
                
            #Else, print error
            else:               
                raise TypeError('Organisation input should contain Name ' \
                                f'objects or str, found {type(names[0])}')
        
        #Construction from single name string
        elif isinstance(names, str):
            self.names = Name(names, titles, genders, kwargs) 

        #Construction from single Name object
        elif isinstance(names, Name):
            self.names = names
            
        #Else, print error
        else:
            raise TypeError('List should contain Name objects or str,' \
                            f' found {type(names[0])}')
        
        print(f'Organisation defined with {len(self.names)} names')

    
    def getAllNames(self, all_formats=True):
        """Retrieve all names in Organisation
        
        Parameters
        ----------
        all_formats : bool, default True
          Flag to signify if all name formats should be returned (True), or 
          full names only (False)
        
        Returns
        -------
        all_names : list
          List of all organisation names
        """
        all_names=[]
        for n in self.names:
            if all_formats == True:
                all_names.append(n.getAllNameFormats())
            else:
                all_names.append(n.fullname)
        return all_names
    
    
    def checkOrgName(self, n):
        """Check if name is in Organisation
        
        Parameters
        ----------
        n : str
          Name to check
        
        Returns
        -------
        check : str or None
          Name string that input name matches with, or None if there is no 
          match
        """
        check=None
        for name in self.names:
            if name.matchName(n):
                check=name
        if check==None:
            return None
        else:
            return check
        
        
    def populateOrg(self, scopus=True, scholar=True):
        """Populate Organisation with additional information gathered from 
        Scopus and/or Scholar
        
        Parameters
        ----------
        scopus : bool, default True
          Flag to denote if Scopus authors should be used to populate object
        scholar : bool, default True
          Flag to denote if Scholar authors should be used to populate object
        """
        for n in self.names:
            if scopus == True:
                n.populateFromScopus()
            if scholar == True:
                n.populateFromScholar()
            
    
    def addName(self, n, t=None, g=None, **kwargs):
        """Add name to Organisation
        
        Parameters
        ----------
        n : Name or str or list           
          Name to add, given as eiter Name, fullname string, or 
          fullname list [firstname, middlename, lastname]
        t : str, optional 
          Title
        g : str, optional
          Gender 
        **kwargs : dict
          Keyword arguments (valid keywords: orcid, scholarid, scopusid, 
          hindex_scopus, hindex_scholar, affiliation)         
        """
        #If Name object given
        if isinstance(n, Name):
            new = n       
        
        #If fullname string or list [first, middle, last] given
        elif isinstance(n, list) or isinstance(n, str):
            new = Name(n, t, g, kwargs)
        
        #Else, pass 
        else:
            raise TypeError('Invalid name type {type(args)} given. ' \
                            'Expected str, list or Author object.') 
        
        #Append new author
        self.names.append(new)
                       
        
    def asDataFrame(self):
        """Export Organisation as dataframe
        
        Returns
        -------
        df : pandas.DataFrame
          Organisation attributes as dataframe
        """
        df = pd.DataFrame()
        for a in self.names:
            df = df.append({'full_name': a.fullname,
                            'title': a.title,
                            'guessed_gender': a.getGender(),
                            # 'affiliation': a.affiliation,
                            'orcid_id': a.orcid,
                            'scholar_id': a.scholarid,
                            'scopus_id': a.scopusid,
                            'full_initials': a.getFullInitials(),
                            'single_initials': a.getSingleInitials(),
                            'partial_initials': a.getNameAndInitials(),
                            'only_first': a.getSingleName(),
                            'h-index_scopus': a.hindex_scopus,
                            'h-index_scholar': a.hindex_scholar},
                            ignore_index=True)           
        return df
    
    
    def checkNames(self): 
        """Checker and user editor for names and genders in Organisation
        """
        #Begin loop
        r1='n'
        while True:
            
            #Show revised organisation
            df = self.asDataFrame()
            print(df[['full_name', 'full_initials', 'guessed_gender']])
            
            #User prompted editing, proceed if 'n'
            r1 = input ('Is the organisation correct? [y/n] ')
            if r1 in ['n']:
                
                #Identify name object to change
                r2 = input (f'Which author is incorrect? [0-{len(df.index)-1}] ')
                if 0 <= int(r2) <= len(df.index):
                    a = self.names[int(r2)]
                    print(f'\nAuthor {a.fullname} \nFirst name: {a.firstname}'\
                          f'\nMiddle name: {a.middlename} '\
                          f'\nSurname: {a.surname} \nGender: {a.gender}')
                    
                    #Prompt first name alteration
                    first = input(f'First name {a.firstname} >> ')
                    if first != '':
                        a.firstname = str(first)
                        
                    #Prompt middle name alteration    
                    middle = input(f'Middle names {a.middlename} ["none" ' \
                                   'for no middle name] >> ')
                    if middle != '':
                        if middle == 'none':
                            a.middlename = None
                        else:    
                            a.middlename = str(middle)
                     
                    #Prompt surname alteration    
                    surname = input(f'Surname {a.surname} >> ')
                    if surname != '':
                        a.surname = str(surname)
                    
                    #Prompt gender alteration
                    gender = input(f'Gender {a.gender} [m/f/nb] >> ')
                    if gender in ['f', 'm', 'nb']:
                        if gender == 'f':
                            a.gender='female'
                        elif gender == 'm':
                            a.gender='male'
                        else:
                            a.gender='nb'
           
            #Exit if 'y'
            elif r1 in ['y']: 
                break
        

#------------------------------------------------------------------------------    
       
def lookupName(n, names):
    """Check if name is in list of names
    
    Parameters
    ----------
    n : str
      Name to check
    names : list
      List of names to check in
    
    Returns
    -------
    bool
      Flag denoting if name has been found in list (True) or not (False)
    """
    if n in names:
        return True
    else:
        return False


def checkGender(name, organisation):
    """Check if name appears in Organisation and if so, return gender
    
    Parameters
    ----------
    name : str
      Name to check
    organisation : Organisation
      Organisation object to check if name and genderappears in
    
    Returns
    -------
    gender  : str or None
      Gender of name, or None if name does not appear in Organisation object
    """
    gender=None
    for n in organisation.names:
        all_n = n.getAllNameFormats()
        if name in all_n:
            gender = n.gender
    return gender


def checkAffiliation(name, organisation):
    """Check if name appears in Organisation and if so, return affiliation
    
    Parameters
    ----------
    name : str
      Name to check
    organisation : Organisation
      Organisation object to check if name and genderappears in
    
    Returns
    -------
    aff  : str or None
      Affiliation of name, or None if name does not appear in Organisation 
      object
    """
    aff=None
    for n in organisation.names:
        all_n = n.getAllNameFormats()
        if name in all_n:
            aff = n.affiliation
    return aff


def orgFromCSV(csv_file):
    """Import organisation from csv file
    
    Parameters
    ----------
    csv_file : str                  
      Filepath to csv organisation
    
    Returns
    -------
    org : Organisation
      Organisation object
    """
    #Setup gender database from file
    database = pd.read_csv(csv_file)
    n_db = list(database['full_name'])
    t_db = list(database['title'])
    g_db = list(database['guessed_gender'])
    org = Organisation(n_db, t_db, g_db)
    return org
