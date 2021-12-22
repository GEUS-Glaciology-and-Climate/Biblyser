'''
Biblyser (c) is a bibliometric workflow for evaluating the bib metrics of an 
individual or a group of people (an organisation).

Biblyser is licensed under a MIT License.

You should have received a copy of the license along with this work. If not, 
see <https://choosealicense.com/licenses/mit/>.

BIBLYSER SETUP FILE
This file is needed for the package installation.
'''

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="biblyser", 
    version="0.0.1",
    author="Penelope How",
    author_email="pho@geus.dk",
    description="A bibliometric workflow for evaluating the bib metrics of an individual or group of people",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GEUS-Glaciology-and-Climate/Biblyser",
    project_urls={
        "Bug Tracker": "https://github.com/GEUS-Glaciology-and-Climate/Biblyser/issues",
    },
    keywords="publications citations academia science bibliometrics",
#    package_dir={"": "Biblyser"},
#    packages=setuptools.find_packages(where="Biblyser"),
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering",
        "Operating System :: OS Independent",
    ],
    install_requires=['gender-guesser', 'habanero', 'numpy', 'pandas', 'pybliometrics', 'scholarly'],
    python_requires='>=3.7',
)

