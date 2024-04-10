Hello,

Here are the instructions to all you need to install
- QGIS
- miniconda
- hydro-mt
- SFINCS

** QGIS **
QGIS very simple to download:
- Google QGIS download 
- or copy this link: https://www.qgis.org/nl/site/forusers/download.html

For instructions how to use QGIS, go to youtube and search 'Hans van der Kwast QGIS'. He is very instructional.


** miniconda**
For miniconda to download you can follow this link: 
https://docs.anaconda.com/free/miniconda/index.html

You only really need miniconda to install hydro-mt. 


** hydro-mt **
Hydro-mt is a Python package developed by Deltares. In this map is a downloadable package of hydro-mt. For the latest version contact deltares. 

-Open the map Deltares-hydromt_sfincs-73534c5
-Open READMEhydromt

Follow the instructions, yet do this in miniconda Anaconda prompt if they do not work in your normal Anaconda prompt.
Here are the instructions again:

To install hydromt_sfincs using pip do:

.. code-block:: console

  pip install hydromt_sfincs

We recommend installing a hydromt-sfincs environment including the hydromt_sfincs package
based on the environment.yml file. This environment will install all package dependencies 
including the core of hydroMT_.

.. code-block:: console

  conda env create -f binder/environment.yml
  conda activate hydromt-sfincs
  pip install hydromt_sfincs

To use hydro-mt after installation, open Anaconda navigator and select hydro-mt as your environment. Then open VS code to use Tool1 and Tool2

** SFINCS **

SFINCS is a program developed by Deltares. It is also in the zip-file already and should run with the help from Tool 2. 
You can also contact Deltares for the latest installation. 
