"""
PyBiblyser (c) is a bibliometric workflow for evaluating the bib metrics of an 
individual or a group of people (an organisation).

PyBiblyser is licensed under a MIT License.

You should have received a copy of the license along with this work. If not, 
see <https://choosealicense.com/licenses/mit/>.
"""

import pandas as pd
from Name import Name, getKeyValue

#------------------------------------------------------------------------------    

class Organisation(object):
    '''The Organisation object holds a collection of Name objects, 
    representing an institution or department'''
    
    def __init__(self, names, titles=None, genders=None, **kwargs):
        '''Initialise organisation from list of names
        
        Variables
        names (list)                List of str names or Name objects
        titles (list)               List of str titles (default=None)
        genders (list)              List of str genders (default=None)
        **kwargs                    Keyword arguments (valid keywords: orcid, 
                                    scholarid, scopusid, hindex_scopus, 
                                    hindex_scholar, affiliation)        
        '''
        print(f'Constructing Organisation from {type(names)}')
        if isinstance(names, list): 
            
            #Construction from list of Name objects
            if isinstance(names[0], Name):
                self._names = names
                
            #Construction from list containing name strings                
            elif isinstance(names[0], str) or isinstance(names[0], list): 
                new=[]
                for i in range(len(names)):
                    new_name = Name(names[i])
                    if titles != None:
                        new_name._title = titles[i]
                    if genders != None:
                        new_name._gender = genders[i]
                        
                    try:
                        new_name._orcid = getKeyValue(kwargs, 'orcid')[i]
                        new_name._scopusid = getKeyValue(kwargs, 'scopusid')[i]
                        new_name._hindex_scopus = getKeyValue(kwargs, 
                                                              'hindex_scopus')[i]
                        new_name._hindex_scholar = getKeyValue(kwargs, 
                                                               'hindex_scholar')[i]
                    except:
                        self._orcid = None
                        self._scopusid = None
                        self._hindex_scopus = None
                        self._hindex_scholar = None
                    new.append(new_name)
                    
                self._names = new
                
            #Else, print error
            else:               
                raise TypeError('Organisation input should contain Name ' \
                                f'objects or str, found {type(names[0])}')
        
        #Construction from single name string
        elif isinstance(names, str):
            self._names = Name(names, titles, genders, kwargs) 

        #Construction from single Name object
        elif isinstance(names, Name):
            self._names = names
            
        #Else, print error
        else:
            raise TypeError('List should contain Name objects or str,' \
                            f' found {type(names[0])}')
        
        print(f'Organisation defined with {len(self._names)} names')

    
    def getAllNames(self, all_formats=True):
        '''Retrieve all names in Organisation'''
        all_names=[]
        for n in self._names:
            if all_formats == True:
                all_names.append(n.getAllNameFormats())
            else:
                all_names.append(n._fullname)
        return all_names
    
    
    def checkOrgName(self, n):
        '''Check if name is in Organisation'''
        check=None
        for name in self._names:
            if name.matchName(n):
                check=name
        if check==None:
            return None
        else:
            return check
        
        
    def populateOrg(self, scopus=True, scholar=True):
        '''Populate Organisation with additional information gathered from 
        Scopus and/or Scholar'''
        for n in self._names:
            if scopus == True:
                n.populateFromScopus()
            if scholar == True:
                n.populateFromScholar()
            
    
    def addName(self, n, t=None, g=None, **kwargs):
        '''Add name to Organisation
        
        Variables
        n (Name/str/list)           Name to add         
        titles (list)               Title (default=None)
        genders (list)              Gender (default=None)
        **kwargs                    Keyword arguments (valid keywords: orcid, 
                                    scholarid, scopusid, hindex_scopus, 
                                    hindex_scholar, affiliation)         
        '''
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
        self._names.append(new)
                       
        
    def asDataFrame(self):
        '''Export Organisation as dataframe'''
        df = pd.DataFrame()
        for a in self._names:
            df = df.append({'full_name': a._fullname,
                            'title': a._title,
                            'guessed_gender': a.getGender(),
                            'orcid_id': a._orcid,
                            'scholar_id': a._scholarid,
                            'scopus_id': a._scopusid,
                            'full_initials': a.getFullInitials(),
                            'single_initials': a.getSingleInitials(),
                            'partial_initials': a.getNameAndInitials(),
                            'only_first': a.getSingleName(),
                            'h-index_scopus': a._hindex_scopus,
                            'h-index_scholar': a._hindex_scholar},
                            ignore_index=True)           
        return df
    
    
    def checkNames(self): 
        '''Checker and user editor for names and genders in Organisation'''  
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
                    a = self._names[int(r2)]
                    print(f'\nAuthor {a._fullname} \nFirst name: {a._firstname}'\
                          f'\nMiddle name: {a._middlename} '\
                          f'\nSurname: {a._surname} \nGender: {a._gender}')
                    
                    #Prompt first name alteration
                    first = input(f'First name {a._firstname} >> ')
                    if first != '':
                        a._firstname = str(first)
                        
                    #Prompt middle name alteration    
                    middle = input(f'Middle names {a._middlename} ["none" ' \
                                   'for no middle name] >> ')
                    if middle != '':
                        if middle == 'none':
                            a._middlename = None
                        else:    
                            a._middlename = str(middle)
                     
                    #Prompt surname alteration    
                    surname = input(f'Surname {a._surname} >> ')
                    if surname != '':
                        a._surname = str(surname)
                    
                    #Prompt gender alteration
                    gender = input(f'Gender {a._gender} [m/f/nb] >> ')
                    if gender in ['f', 'm', 'nb']:
                        if gender == 'f':
                            a._gender='female'
                        elif gender == 'm':
                            a._gender='male'
                        else:
                            a._gender='nb'
           
            #Exit if 'y'
            elif r1 in ['y']: 
                break
        

#------------------------------------------------------------------------------    
       
def lookupName(n, names):
    '''Check if name is in list of names
    
    Variables
    n (str)                         Name
    names (list)                    List of names
    '''
    if n in names:
        return True
    else:
        return False


def checkGender(name, organisation):
    '''Check if name appears in Organisation and if so, return gender
    '''
    gender=None
    for n in organisation._names:
        all_n = n.getAllNameFormats()
        if name in all_n:
            gender = n._gender
    return gender


def orgFromCSV(csv_file):
    '''Import organisation from csv file
    
    Variables
    csv_file (str)                  Filepath to csv organisation
    
    Returns
    org (Organisation)              Organisation object
    '''
    #Setup gender database from file
    database = pd.read_csv(csv_file)
    n_db = list(database['full_name'])
    t_db = list(database['title'])
    g_db = list(database['guessed_gender'])
    org = Organisation(n_db, t_db, g_db)
    return org