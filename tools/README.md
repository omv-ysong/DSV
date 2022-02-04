# DSV tools
This folder contains some useful tools for creating or processing the data in this dataset.

(1) convert_disparity_to_depth.py

Usage: convert Middlebury disparity image (.pfm) to depth image (.exr) with real world depth values. 

Example: python convert_disparity_to_depth.py --pfmPath ./disp0.pfm --calibPath ./calib.txt --exrPath ./disp0.exr
