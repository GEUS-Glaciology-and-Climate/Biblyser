Installation
============

Quickstart
----------

Clone `this repository <https://github.com/GEUS-Glaciology-and-Climate/pyBiblyser>`_ into your local directory

.. code-block:: python

   git clone https://github.com/GEUS-Glaciology-and-Climate/pyBiblyser

Create a conda environment with the required package dependencies, either using the environment file provided in the repository.

.. code-block:: python

   conda env create --file environment.yml


Or by installing the packages into your conda environment with pip

.. code-block:: python

   pip install pybyliometrics, habanero, scholarly, gender_guesser, pandas


Scopus API configuration
------------------------

An API key or Insttoken is needed to use the Scopus API. An API key can be generated through the Elsevier Developer Portal `here <https://dev.elsevier.com/apikey/manage>`_, which can be used to access all authors and publications within your organisation when in your network or through VPN access. If accessing this from within the network is challenging, then an Insttoken can be requested by contacting Elsevier directly. 

Use the configuration functionality in pybliometrics to set up the configuration to the Scopus API

.. code-block:: python

   # Import pybliometrics (which includes the Scopus API)
   import pybliometrics

   # Set up Scopus configuration (only needs to be done once)
   pybliometrics.scopus.utils.create_config()

See the `pybliometrics readthedocs <https://pybliometrics.readthedocs.io/en/stable/configuration.html>`_ for more information on this configuration.
