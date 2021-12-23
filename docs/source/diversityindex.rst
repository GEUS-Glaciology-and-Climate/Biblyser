Diversity Index
===============

The computed bibcollection metrics can be used to determine a diversity index for an individual or organisation. This diversity index is based on the gender and affiliation/country composition in all publication authorships. Generally, this is determined from publications in the last five years, but can be changed as an optional parameter. 

.. code-block:: python

   from biblyser.bibcollection import calcDivIdx

   calcDivIdx('Penelope How',    #Name
   	      5,                 #Years to calculate
	      scopus=True,       #Bibs from scopus
	      scholar=False,     #from scholar
	      crossref=False,    #from crossref
              check=True)        #User check bibs?

An example script for calculating diveristy index is available in the Github repository [here](https://github.com/GEUS-Glaciology-and-Climate/Biblyser/blob/main/biblyser/examples/getDiv.py), which can be run from the command line. 

.. code-block:: python

   python getDiv calcDivIdx --name "Penelope How"

