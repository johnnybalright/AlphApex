"""
This module contains constants defining file paths and URLs necessary
for a GIS-related project.

Paths included refer to the location of shapefiles, TIFF files, and
text files used in the project:
- EB_LINE: Path to the eastbound line shapefile.
- WB_LINE: Path to the westbound line shapefile.
- IN_SHP_MAIN: Path to the main input shapefile.
- IN_SHP_MAIN_SUBSET: Path to a subset of the main input shapefile.
- IN_DEM_MAIN: Path to the main Digital Elevation Model (DEM) TIFF file.
- XML_LINKS: Path to a text file containing XML links.
- BOUND_COORDS: Path to a text file containing boundary coordinates.

URLs included refer to various metadata located on the USGS FTP server.
These URLs point to metadata
pertaining to elevation projects across various counties, such as
Suwannee, Columbia, Lafayette, and
others.

All paths and URLs are hardcoded and point to specific locations or
files necessary for the execution and completion of the GIS project.
"""
# EB_LINE="https://linode-bucket-1.us-southeast-1.linodeobjects.com/gis_data/suw_eb_line.geojson"
EB_LINE="/mnt/ubuntu-storage-2/gis/suw_eb_line.shp"
# WB_LINE="https://linode-bucket-1.us-southeast-1.linodeobjects.com/gis_data/suw_wb_line.geojson"
WB_LINE="/mnt/ubuntu-storage-2/gis/suw_wb_line.shp"
# EFLDWY="https://linode-bucket-1.us-southeast-1.linodeobjects.com/gis_data/efldwy_l.geojson"
EFLDWY="/mnt/ubuntu-storage-2/gis/efldwy_l.shp"
# WFLDWY="https://linode-bucket-1.us-southeast-1.linodeobjects.com/gis_data/wfldwy_l.geojson"
WFLDWY="/mnt/ubuntu-storage-2/gis/wfldwy_l.shp"
# SUW="https://linode-bucket-1.us-southeast-1.linodeobjects.com/gis_data/suw_cut.geojson"
SUW="/mnt/ubuntu-storage-2/gis/suw_cut.shp"
# SUW_XS="https://linode-bucket-1.us-southeast-1.linodeobjects.com/gis_data/suw_xs.geojson"
SUW_XS="/mnt/ubuntu-storage-2/gis/suw_xs.shp"
# IN_SHP_MAIN_SUBSET="https://linode-bucket-1.us-southeast-1.linodeobjects.com/gis_data/subset_parcels20.geojson"
IN_SHP_MAIN_SUBSET="/mnt/ubuntu-storage-2/gis/subset_parcels20.shp"
IN_SHP_MAIN_SUBSET_2="/mnt/ubuntu-storage-2/gis/subset_parcels20_2.shp"
# IN_DEM_MAIN="https://linode-bucket-1.us-southeast-1.linodeobjects.com/gis_data/dem2019.tiff"
IN_DEM_MAIN="/mnt/ubuntu-storage-2/gis/dem2019.tiff"
# PARQUET_PARCELS_20="https://linode-bucket-1.us-southeast-1.linodeobjects.com/gis_data/parcels20.parquet"
PARQUET_PARCELS_20="/mnt/ubuntu-storage-2/gis/parcels20.parquet"
# LPC_GRID="https://linode-bucket-1.us-southeast-1.linodeobjects.com/gis_data/srmwd_lpc_grid.geojson"
LPC_GRID="/mnt/ubuntu-storage-2/gis/srwmd_lpc_grid.shp"
XML_LINKS="./tmp/xml_links.txt"
BOUND_COORDS="./tmp/bound_coords.txt"
USGS_METADATA_FTP_SUWANNEE="https://rockyweb.usgs.gov/vdelivery/Datasets/" \
    + "Staged/Elevation/LPC/Projects/FL_Peninsular_FDEM_2018_D19_DRRA/" \
        + "FL_Peninsular_FDEM_Suwannee_2018/metadata/"
USGS_METADATA_FTP_COLUMBIA="https://rockyweb.usgs.gov/vdelivery/Datasets/" \
    + "Staged/Elevation/LPC/Projects/FL_Peninsular_FDEM_2018_D19_DRRA/" \
        + "FL_Peninsular_FDEM_Columbia_2018/metadata/"
USGS_METADATA_FTP_LAFAYETTE="https://rockyweb.usgs.gov/vdelivery/Datasets/" \
    + "Staged/Elevation/LPC/Projects/FL_Peninsular_FDEM_2018_D19_DRRA/" \
        + "FL_Peninsular_FDEM_Lafayette_2018/metadata/"
USGS_METADATA_FTP_GILCHRIST="https://rockyweb.usgs.gov/vdelivery/Datasets" \
    + "/Staged/Elevation/LPC/Projects/FL_Peninsular_FDEM_2018_D19_DRRA" \
    + "/FL_Peninsular_FDEM_Gilchrist_2018/metadata/"
USGS_METADATA_FTP_DIXIE="https://rockyweb.usgs.gov/vdelivery/Datasets/" \
    + "Staged/Elevation/LPC/Projects/FL_Peninsular_FDEM_2018_D19_DRRA/" \
        + "FL_Peninsular_FDEM_Dixie_2018/metadata/"
USGS_METADATA_FTP_LEVY="https://rockyweb.usgs.gov/vdelivery/Datasets/" \
    + "Staged/Elevation/LPC/Projects/FL_Peninsular_2018_D18/" \
        + "FL_Peninsular_Levy_2018/metadata/"
USGS_METADATA_FTP_MADISON="https://rockyweb.usgs.gov/vdelivery/Datasets/" \
    + "Staged/Elevation/LPC/Projects/FL_Peninsular_FDEM_2018_D19_DRRA/" \
        + "FL_Peninsular_FDEM_Madison_2018/metadata/"
USGS_METADATA_FTP_HAMILTON="https://rockyweb.usgs.gov/vdelivery/Datasets/" \
    + "Staged/Elevation/LPC/Projects/FL_Peninsular_FDEM_2018_D19_DRRA/" \
        + "FL_Peninsular_FDEM_Hamilton_2018/metadata/"
FLOOD_REPORT_URL='https://www.srwmdfloodreport.com/'
SUWANNEE_PARCEL_URL='http://www.suwanneepa.com/gis/'
COLUMBIA_PARCEL_URL='http://g4.columbia.floridapa.com/gis/'
LAFAYETTE_PARCEL_URL="http://www.lafayettepa.com/gis/"
GILCHRIST_PARCEL_URL = (
    "https://qpublic.schneidercorp.com/"
    + "Application.aspx?AppID=820&LayerID=15174&"
    + "PageTypeID=4&PageID=6883&KeyValue="
)
GILCHRIST_MAP_URL = (
    "https://qpublic.schneidercorp.com/"
    + "Application.aspx?AppID=820&LayerID=15174&"
    + "PageTypeID=1&PageID=6880&KeyValue="
)
DIXIE_PARCEL_URL = (
    "https://qpublic.schneidercorp.com/Application."
    + "aspx?AppID=867&LayerID=16385&PageTypeID=2&PageID=7230&"
    + "KeyValue="
)
DIXIE_MAP_URL = (
    "https://qpublic.schneidercorp.com/Application."
    + "aspx?AppID=867&LayerID=16385&PageTypeID=1&"
    + f"PageID=7229&KeyValue="
)
LEVY_PARCEL_URL = (
    "https://qpublic.schneidercorp.com/"
    + "Application.aspx?AppID=930&LayerID=18185&PageTypeID=4&"
    + f"PageID=8127&KeyValue="
)
LEVY_MAP_URL = (
    "https://qpublic.schneidercorp.com/Application"
    + ".aspx?AppID=930&LayerID=18185&PageTypeID=1&PageID=8124&"
    + f"KeyValue="
)
HAMILTON_PARCEL_URL = (
    "https://beacon.schneidercorp.com/Application"
    + ".aspx?AppID=817&LayerID=14544&PageTypeID=4&PageID=6411"
    + f"&KeyValue="
)
HAMILTON_MAP_URL = (
    "https://beacon.schneidercorp.com/Application."
    + "aspx?AppID=817&LayerID=14544&PageTypeID=1&PageID=6408"
    + f"&KeyValue="
)
MADISON_PARCEL_URL = (
    "https://qpublic.schneidercorp.com/"
    + "Application.aspx?AppID=911&LayerID=17548&PageTypeID=4&"
    + f"PageID=7848&KeyValue="
)
MADISON_MAP_URL = (
    "https://qpublic.schneidercorp.com/Application."
    + "aspx?AppID=911&LayerID=17548&PageTypeID=1&PageID=7845&"
    + f"KeyValue="
)
