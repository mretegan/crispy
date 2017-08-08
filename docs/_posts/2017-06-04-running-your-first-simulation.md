---
layout: post
title: Running your first simulation.
---

## 1. generate XANES spectra
---

An example of Mn metal K pre-edge simulation is shown in the this tutorial and the content includes:

> - **Parameters set-up**
> - **Run simulations and read Quanty output files**
> - **Save the spectra data and graph**
> - **Run multi-calculations and merge data**
> - **Save calculation and Quanty input files**


#### 1.1 Parameters set-up

**1.** Run Crispy software and you can see the interface as follows. There are four folded panels on the right side. In **General Setup**, you can choose the metal element that you want to calculate. In our first tutorial, we are going to calculate K pre-edge XANES for Mn(II) compound. So in **Elment and Symmetry** we click on **Mn**.  

![]({{ site.url }}/img/tutorial/crop_1.png) 


**2.** Then we can choose the oxidation state and symmetry. So far only octahedral (**Oh**) and elongated octahedral (**D4h**) are available in Crispy. In the future work, we are going to implement more symmetry choices. In the **Experiment and Edge** set-up, we keep XAS and K-edge choice.


![]({{ site.url }}/img/tutorial/crop_3.png)


**3.** Above are the basic parameters. Now we switch to the second parameter panel **States and Spectrum Parameters**, we keep the default values. It's worth noting that Quanty doesn't give correct absolute **absorption energy**. What we are interested are the spectral features and the relative absorption energies, so that one should calibrate/shift the absorption energy in respect to experiment measurements. If more precised spectra data is needed, increase the **Number of Points**. The **Gamma FWHM** is the life-time broadening.


![]({{ site.url }}/img/tutorial/crop_5.png)


**4.** The **Hamiltonian Setup** is the soul of the simulation. So far, four Halmitonians set-ups are available in Crispy:

- **Coulomb:** more detailed description → *[Click Here](http://www.quanty.org/documentation/standard_operators/coulomb_repulsion)*
- **Spin-Orbit Coupling:** more detailed description → *[Click Here](http://www.quanty.org/documentation/standard_operators/spin_orbit_coupling)*
- **Crystal Field:** more detailed description → *[Click Here](http://www.quanty.org/documentation/standard_operators/crystal_field)*
- **3d-Ligands Hybridization:** more detailed description → *[Click Here](http://www.quanty.org/documentation/standard_operators/ligand_field)*


By double click the Parameter Value, one can change the parameters into the values of interest. In our first tutorial, we keep the default values.


![]({{ site.url }}/img/tutorial/crop_6.png)


Crystal field default value is 1.0 now.


![]({{ site.url }}/img/tutorial/crop_7.png)


#### 1.2 Running simulations and reading Quanty output files

**1.** After setting all the parameters, we can simply click the **Run** button to carry out the calculation. When the calculation is done, the generated spectrum is automatically plotted in the left panel. By clicking the buttons on the plotting panel, one can change the plotting style/scale/colors.


![]({{ site.url }}/img/tutorial/crop_8.png)


![]({{ site.url }}/img/tutorial/crop_9.png)


**2.** Drag up the bottom of the plotting, and the output file is printed for Quanty. By looking at the output file, one can find the initial state / final state Halmitonian information.


![]({{ site.url }}/img/tutorial/crop_10.png)


#### 1.3 Save the spectra data and graph

**1.** By clicking the **Save** button, the generated spectra can be saved into images or .txt files so that the data can be further processed by other softwares.


![]({{ site.url }}/img/tutorial/crop_12.png)


#### 1.4 Run multi-calculations and merge data

**1.** One of the greatest advantage of Crispy is the ability of running multiple calculations. And this greatly facilitate playing around with different parameters. When we want to run another calculation, we can simply go back to parameter panels. For example, I selected another oxidation state Mn(III).


![]({{ site.url }}/img/tutorial/crop_13.png)


**2.** After changing the parameters, we find one more Calculation 
**Mn 3+ Oh XAS K(1s)** 
in the results panel. If we want to check the detailed parameters for one of the calculation result, we can click on it and the values in corresponding parameter panels will automatically changed to the values we set for that specific calculation.


![]({{ site.url }}/img/tutorial/crop_14.png)


**3.** By selecting both results, we can merge different spectra.


![]({{ site.url }}/img/tutorial/crop_15.png)   


#### 1.5 Save calculation and Quanty input files

**1.** In **Part 1.4**, we already showed how to run multiple calculations. Assumed that we have ran a lot of calculations, we want to save a series of calculations with their corresponding parameters. And this can be done by right clicking **Save Selected Calculations As** a .pkl file. Therefore, when restarting the program, we can choose **Load Calculations** to load the .pkl file to recover the status before.


![]({{ site.url }}/img/tutorial/crop_16.png)


![]({{ site.url }}/img/tutorial/crop_17.png)
   
   
**2.** Quanty is written in LUA language. And Crispy is able to generate Quanty input file. This is useful to modify some scripts for more specific/personalized calculations adding the Halmitonian terms which aren't implemented in the interface.


![]({{ site.url }}/img/tutorial/crop_11.png)
