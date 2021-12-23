Guide
=====

Name
----

The Name object holds attributes about an individual to aid in searching for associated publications. This can be initialised using an individual's full name, with job title and gender as optional inputs, and additional keyword inputs for Orcid ID, Scopus ID, Google Scholar ID, and h-index. 
   
.. code-block:: python

   from biblyser.name import Name
	
   # With fullname string
   n = Name('Jane Emily Doe')
	
   # With first, middle and last name as list 		
   n = Name (['Jane','Emily','Doe']) 	 
	
   # With name and additional information
   n = Name('Jane Emily Doe', 'Forsker', 'female', orcid='0000-0001-2345-6789') 

Various name and initial formats are computed from Name object, which maximise the chance of finding all associated publications. The gender of each name can either be provided during initialisatoin, or guessed using `gender_guesser`. The gender definition is used later on to analyse gender distribution in a **BibCollection**.


Organisation
------------

The Organisation object holds a collection of **Name** objects which represent a group of authors, department, or organisation. The GEUS G&K organisation can be fetched either from the GEUS G&K Pure portal (only retrieves registered authors) or from the staff directory webpage (all G&K members). This information is fed directly into an Organisation object.

.. code-block:: python

   from biblyser.organisation import Organisation, fetchWebInfo

   def fetchWebInfo(url, parser, fid, classtype, classid):
       '''Get all up-to-date information (e.g. names, titles) from a 
       given webpage element id and class'''
       page = requests.get(url)
       soup = BeautifulSoup(page.content, parser)
       results = soup.find(id=fid)
       elements = results.find_all(classtype, class_=classid)
       return elements
    
   # Get names and titles from organisation Pure portal
   URL = "https://pub.geus.dk/da/organisations/department-of-glaciology-and-climate/persons/"
   info = fetchWebInfo(URL, 'html.parser', 'main-content', 'div', 
                       'rendering rendering_person rendering_short rendering_person_short')
   names=[]
   titles=[]
   [names.append(str(e).split('span')[1].split('<')[0].split('>')[1]) for e in info]
   [titles.append(str(e).split('span')[5].split('<')[0].split('- ')[1]) for e in info]


   # Get names and titles from organisation staff page
   URL = "https://www.geus.dk/om-geus/kontakt/telefonbog?departmentId=Glaciologi+og+Klima"
   names = fetchWebInfo(URL, 'html.parser',  'gb_ContentPlaceHolderDefault_bottomGrid_ctl03', 
                        'td', 'contact-name')
   titles = fetchWebInfo(URL, parser, fid, classtype, None)
   titles = info[:][4]

   # Define organisation
   org = Organisation(names, titles)               

The Organisation object has a checker, which requires user input to manually edit Name objects - this is especially useful in cases of abnormal surname structures and mis-gendered Names. Once satisfied with the information held in the Organisation object, the Organisation object can be populated with missing information from Scopus and Scholar. The final populated object can either be written out of the object as a DataFrame, or carried forward and used to gather bib information as a **BibCollection**.

.. code-block:: python

   # Organisation checker
   org.checkNames()

   # Populate author info from Scopus and Scholar                         
   org.populateOrg()

   # Write Organisation attributes to DataFrame
   df = org.asDataFrame()

Bib
---

A Bib object holds the relevant information associated with a single publication, namely:

+ DOI
+ Publication title
+ Authors (held as **Name** objects)
+ Date of publication
+ Journal title
+ Publication type
+ Gender metrics 
+ Citation count
+ Altmetric record

A Bib object can either be initiated from a doi string, a title string, or from an author/organisation (as part of a **BibCollection**, see relevant section).

.. code-block:: python

   from biblyser.bib import Bib

   # Bib object from doi string
   pub = Bib(doi='10.5194/tc-11-2691-2017') 		

   # Bib object from publication title
   pub = Bib(title='PyTrx: A Python-Based Monoscopic Terrestrial' \
             'Photogrammetry Toolset for Glaciology')

Bib attributes are populated using the Scopus API provided by [
`pybliometrics <https://pybliometrics.readthedocs.io/en/stable/>`_, CrossRef API provided by `habanero <https://habanero.readthedocs.io/en/latest/index.html>`_, and/or the Google Scholar API (`scholarly <https://scholarly.readthedocs.io/en/stable/quickstart.html>`_).

Authorship of a publication can be queried within the Bib object, including queries by **Organisation** and (guessed) gender.


BibCollection
-------------

A BibCollection object holds a collection of **Bib** objects, i.e. a database of all associated or selected publications. A BibCollection can be initialised from an **Organisation** (for which the BibCollection will search for all publications linked to each name in the organisation), a list of **Bib** objects, or a list of doi strings.

.. code-block:: python

   from biblyser.organisation import Organisation
   from biblyser.bibcollection import BibCollection

   # BibCollection from an Organisation
   names = ['Penelope How', 'Nanna B. Karlsson', 'Kenneth D. Mankoff']
   titles = ['AC-medarbejder', 'Seniorforsker', 'Seniorforsker']
   org = Organisation(names, titles)
   pubs = BibCollection(org)

   # Search for bibs in selected databases
   bibs.getScopusBibs()                        #From Scopus (Pure)
   bibs.getScholarBibs()                       #From Google Scholar


   # BibCollection from list of Bib objects
   titles=['PyTrx: A Python-Based Monoscopic Terrestrial Photogrammetry' \
	   'Toolset for Glaciology', 
	   'A first constraint on basal melt-water production of the' \
	   'Greenland ice sheet', 
	   'Greenland ice sheet mass balance from 1840 through next week']
   bibs=[]
   [bibs.append(Bib(title=t)) for t in titles]
   pubs = BibCollection(bibs)


   # BibCollection from list of doi strings
   dois = ['10.3389/feart.2020.00021',
    	   '10.1038/s41467-021-23739-z', 
	   '10.5194/essd-13-5001-2021']
   pubs = BibCollection(dois)

Constructing a BibCollection from an **Organisation** can create duplicates due to common authorships, and create false publications due to common names and tags. Duplicates, false matches and unwanted publications (e.g. conference abstracts, discussion papers) can be removed using the filtering functions provided in the BibCollection objects. 

.. code-block:: python

   # Remove abstracts and discussion papers
   bibs.removeAbstracts()                          
   bibs.removeDiscussions()                       

   # Remove duplicates
   bibs.removeDuplicates()                         

A BibCollection can also be written out of the object as a DataFrame if further inspection is needed

.. code-block:: python

   # Check bibs
   bibs.checkBibs()

   # Remove duplicates
   bibs.removeDuplicates()

   # Write BibCollection attributes to DataFrame
   df = bibs.asDataFrame()

Genders of each author within the Bib object are firstly guessed, and if the guessed gender is not certian then a gender database is used to check if the author and an associated gender exists. This database is an Organisation object, retaining all information about each author's name and gender. If a name is not found in the database then the user is prompted to manually define the gender, and then retains this new addition. 

.. code-block:: python

   import copy

   # Set up gender database using pre-existing organisation
   gdb = copy.copy(org)

   # Guess genders for all co-authors in BibCollection
   bibs.getAllGenders(gdb)
