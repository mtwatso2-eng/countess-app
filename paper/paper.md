---
title: 'Countess: a Shiny web app for automating nematode egg counts'
tags:
  - plant phenotyping
  - image analysis
  - nematode
  - python

authors:
 - name: Mark Watson
   orcid: 0009-0001-6607-880X
   affiliation: 1
 
affiliations:
 - name: University of California, Davis
   index: 1
   
date: 24 July 2025
bibliography: paper.bib
---
 
# Summary

Countess is a web app for automating counts of nematode eggs from counting slide images. A hosted instance of the app can be accessed via a browser at [https://mtwatson-countess.share.connect.posit.cloud/](https://mtwatson-countess.share.connect.posit.cloud/), and the app code can also be run as-is locally or deployed by the user to a Shiny cloud deployment service such as Posit Connect Cloud. The Countess app is built to be accessible to researchers with no coding experience, as it requires no user code to run and has a simple user interface that only requires images from a previously described nematode egg imaging method (Fraher et al., 2024) as inputs. Also, the app uses cloud resources to run its image analysis pipeline, so powerful hardware on the user side is not required.

# Statement of need

We developed this tool in the context of plant breeding for root-knot nematode (_Meloidogyne_ spp.) resistance, for which high-throughput quantitative assays of nematode reproduction are essential. Significance of root-knot nematodes as plant parasites. Need for high-throughput quantitative bioassays, especially in plant breeding programs for resistance. Acknowledge other cases where nematode counting may be useful (including outside of plants). Why counting of eggs, as opposed to other quantification methods? Need for automated counts as opposed to human visual counts for throughput and accuracy.

Existing tools for nematode egg counting, including our previous Countess code in Colab, which is not a web app and uses an older algorithm using an older model. Precedent of shiny apps for other agricultural tasks; how our use case in image analysis is new.

# Design and usage

The Countess app is built on two main components: a Shiny user interface (UI), and a backend image analysis algorithm. The Shiny user interface consists of a button to select a local directory containing nematode counting slide images, an output that displays uploaded images with egg countours drawn on them they are being counted, and a button to download a .csv file of counts. The UI is designed to require minimal resources while remaining scalable to an arbitrary number of images, as it only loads one image to memory at a time and avoids app timeouts as long as counts are being performed. The method to collect counting slide images using Chalex counting slides (Chalex, LLC, Park City, UT), along with the image analysis algorithm that the app uses to detect, classify, and count nematode eggs, are described in (Fraher et al., 2024). The web app takes a folder folder of counting slide images as input, and returns a downloadable data frame of nematode counts corresponding to each image as output. 

# Acknowledgements

This work was supported by the Specialty Crops Research Initiative Grant No. 2021-51181-35865 from the USDA National Institute of Food and Agriculture, the North Carolina Sweetpotato Commission Grant No. GRKN Proposal #22-05, and by a grant from Altria.

# References

Fraher SP, Watson M, Nguyen H, Moore S, Lewis RS, Kudenov M, Yencho GC, Gorny AM. A Comparison of Three Automated Root-Knot Nematode Egg Counting Approaches Using Machine Learning, Image Analysis, and a Hybrid Model. Plant Disease. 2024 Sep 1;108(9):2625-9.

