# Maps and Data

## Required background

In this week's lab we will be make maps with the `cartopy` python package and `matplotlib` within the jupyter notebook environment. We will work though how to download and manipulate the data that we need to use, but we will also need to check that we have downloaded the correct data, that we are reading it correctly and that is is not corrupted. For that there is no better check than plotting a map and taking a good look at the results.

We can contrast the relative ease of access to global datasets with the situation in the 1960s when plate tectonic theory was in its infancy. The data were hard won and difficult to manipulate. The picture of plate tectonics was developed with intuition and receptiveness to 

## The first map: active volcanoes 

This simple code will access geophysical data online, manipulate it, and then use the specified data to make a map of active volcanoes.

Open the notebook: [Notebooks/LAB-Maps+Data/PHYS3070-LabMD.1.1.ipynb](Notebooks/LAB-Maps+Data/PHYS3070-LabMD.1.1.ipynb)


## On-demand data services

This code uses Cartopy which provides access to various of the online mapping services that will serve image data on demand in the form of small image tiles at a specified resolution. The tools automatically query the service and assemble the tiles to make the map but there are some tricks that we need to know before we can use them.

Open the notebook: [Notebooks/LAB-Maps+Data/PHYS3070-LabMD.1.2.ipynb](Notebooks/LAB-Maps+Data/PHYS3070-LabMD.1.2.ipynb)


## Try it out for yourself

This last code will take what you learned in the previous two steps to create a series of nice maps. 


However, this one you'll have to write some of the code yourself!

Open the notebook: [Notebooks/LAB-Maps+Data/PHYS3070-LabMD.1.3.ipynb](Notebooks/LAB-Maps+Data/PHYS3070-LabMD.1.3.ipynb)

## Next steps: 

The data are not just images: we can access the original information and perform calculations. 
In this exercise we make a plot of sea-floor depth against sea-floor age (the most fundamental dataset of the marine plate-tectonics era).

Open the notebook: [Notebooks/LAB-Maps+Data/PHYS3070-LabMD.2.1.ipynb](Notebooks/LAB-Maps+Data/PHYS3070-LabMD.2.1.ipynb) and follow through to the other notebooks in the series:


 -[Notebooks/LAB-Maps+Data/PHYS3070-LabMD.2.2.ipynb](Notebooks/LAB-Maps+Data/PHYS3070-LabMD.2.2.ipynb) 
 -[Notebooks/LAB-Maps+Data/PHYS3070-LabMD.2.3.ipynb](Notebooks/LAB-Maps+Data/PHYS3070-LabMD.2.3.ipynb) 
 -[Notebooks/LAB-Maps+Data/PHYS3070-LabMD.2.4.ipynb](Notebooks/LAB-Maps+Data/PHYS3070-LabMD.2.4.ipynb) 
 -[Notebooks/LAB-Maps+Data/PHYS3070-LabMD.2.5.ipynb](Notebooks/LAB-Maps+Data/PHYS3070-LabMD.2.5.ipynb) 
