<!-- PROJECT LOGO -->
<h3 align="center">Development of a Flood Early Warning System (FEWS) in the Tana River Basin Kenya</h3>

  <p align="center">
    The document serves to aid the visitor in understanding the content and purpose of this project. This project aims to develop both a hydrological (GR4J/SuperflexPy) and hyrodynamic model (SFINCS) to predict flooding in the Tana river near Garissa. The hydrodynamic model currently works using discharge forcing by a telemetric station as input. The SuperflexPy model is currently missing a network structure, but works on a node level.
    <br />
    <a href="https://github.com/pjdebruijn2505/Git_mdp"><strong>Explore the docs »</strong></a>

  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#contact">Data</a></li>
    <li><a href="#contact">Contact</a></li>
    
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project
The models were build as part of a multi-disciplinary-project (MDP) taking place between febuary 2024 and april 2024 over a span of 10 weeks. 5 students from different backgrouds including Hydraulic Engineering, Environmental Engineering and Technology and Policy Management contributed to the project. The used data included data not in the public domain and is therefore not shared, but the models work with other data as well. All models, programs and packages used in the project are Open Source. 

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps.

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/pjdebruijn2505/Git_mdp
   ```
2. Install packages
   ```sh
    conda env create -f FEWS_tana.yml
   ```
3. Install SFINCS (open source)
    ```sh
    https://www.deltares.nl/en/software-and-data/products/sfincs
    ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>
## Data
Data is imported into the notebooks using the file_imports.py located in the utils folder. This way, all notebooks are ensured 
to work after changing only this single file. The file structure should be such that there is a waterlevel folder, a weather data folder and a catchments folder with the shapefiles. By changing this file to point to your own data the rest of the notebooks will all work correctly.

<!-- CONTACT -->
## Contact

Jan van der Wijk - J.vanderWijk@student.tudelft.nl <br>
Patrick de Bruijn - p.j.debruijn@student.tudelft.nl <br>
Mats Kerver - m.r.kerver@student.tudelft.nl <br>
Ivan Temme - I.C.Temme@student.tudelft.nl <br> 
Moniek van Zon - M.S.J.vanZon@student.tudelft.nl <br>

Project Link: https://github.com/pjdebruijn2505/Git_mdp

<p align="right">(<a href="#readme-top">back to top</a>)</p>
