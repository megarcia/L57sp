# L57stack

## Landsat 5/7 stack processing

Code now available, instructions to follow soon!

The best source for the complete Landsat data archive is the [USGS EarthExplorer](https://earthexplorer.usgs.gov/) browser interface.

I built these procedures before the USGS released their "Landsat Collection 1" data product, so I did my own processing of at-satellite radiance measurements to surface reflectance (via *LEDAPS*) and cloud masking (via *Fmask*). My script for that procedure is in the *tools* folder. If you download USGS-processed surface reflectance products for your image stack, you won't need that.

I built these procedures for use with Landsat 5 (TM) and 7 (ETM+) images. These procedures may not be appropriate for use with Landsat 4 (TM) and are definitely not useful for Landsat 8 (OLI) image processing.
