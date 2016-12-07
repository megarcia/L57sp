# L57stack

## Landsat 5/7 stack processing

Code now available, instructions to follow soon!

All scripts and modules (software) included here are licensed for free and fair use under the [Gnu GPL, version 3](https://www.gnu.org/licenses/) (see [LICENSE](./LICENSE_GnuGPLv3.txt) for details). Copyright on the original work (except where noted, especially community contributions) is retained by the author. See also the accompanying [DISCLAIMER](./DISCLAIMER.txt) pertaining to your use of this software.

All python scripts in this package were written for compatibility with python v2.7. We assume no responsibility for differences in functionality (and resulting errors) if you use these scripts with python v3.x. We will, however, attempt to work into ongoing upgrades those fixes compatible with python v3.x that do not break the python v2.7 functionality, so please still report those "bugs" as you find them.

---

The best source for the complete Landsat data archive is the [USGS EarthExplorer](https://earthexplorer.usgs.gov/) browser interface.

I built these procedures before the USGS released their "Landsat Collection 1 Level-1" data product, so I did my own processing of at-satellite radiance measurements to surface reflectance (via *LEDAPS*) and cloud masking (via *Fmask*). My script for that procedure is in the *tools* folder. If you download USGS-processed surface reflectance products for your image stack, you won't need that.

I built these procedures for use with Landsat 5 (TM) and 7 (ETM+) images. These procedures may not be appropriate for use with Landsat 4 (TM) and are definitely not useful for Landsat 8 (OLI) image processing.
