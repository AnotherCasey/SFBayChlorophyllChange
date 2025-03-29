####################################################################################################
#   Chlorophyll Change Automation Script
#   Created by Casey Harper
#   Download and process remote sensing imagery data
#   for chlorophyll-a concentration in San Francisco Bay
#   GEOG 562 Final Project
####################################################################################################

# Import necessary packages
from datetime import date, timedelta
import os
import arcpy
# set the workspace environment
arcpy.env.workspace = r"C:\Users\zombi\Documents\ArcGIS\Projects\GEOG562_Final_Project"
arcpy.env.overwriteOutput = True
## Pull data from online portal and import into ArcGIS project
# Function to get yesterday's date (most recent date for data from online HAB portal)
today = date.today()
yesterday = today - timedelta(days=1)
year, month, day = yesterday.strftime("%Y"), yesterday.strftime("%m"), yesterday.strftime("%d")
print(year, month, day)
# Function to update necessary URLs for get request
def update_url(old_url, year, month, day):
    return old_url.replace("2001", year).replace("13", month).replace("99", day)

try:
        print(f"Yesterday's date: {year}-{month}-{day}")

        urls = {
            "CentralBay": "https://fhab.sfei.org/lib/download.php?request=download&dltype=clipsingle&year=2001&month=13&day=99&product=chlorophyll&composite=max1day&lakename=Central%20Bay",
            "SanPabloBay": "https://fhab.sfei.org/lib/download.php?request=download&dltype=clipsingle&year=2001&month=13&day=99&product=chlorophyll&composite=max1day&lakename=San%20Pablo%20Bay",
            "SouthBay": "https://fhab.sfei.org/lib/download.php?request=download&dltype=clipsingle&year=2001&month=13&day=99&product=chlorophyll&composite=max1day&lakename=South%20Bay",
        }
        updated_urls = {}
        for bay, url in urls.items():
            updated_url = update_url(url, year, month, day)
            updated_urls[bay] = updated_url
except Exception as e:
        print("An error has occurred:", e)
# Specify file path where today's folder will be created
base_path = r"C:\Users\zombi\Documents\ArcGIS\Projects\GEOG562_Final_Project\TIFF_Files"
# Get yesterday's date
yesterday = today - timedelta(days=1)
folder_name = yesterday.strftime('%Y_%m_%d')
# Create full file path
full_path = os.path.join(base_path, folder_name)
# Create folder with yesterday's date within TIFF folder
os.makedirs(full_path, exist_ok=True)
# Check folder successfully created
print(f"Folder '{full_path}' created successfully.")

# Get files from online HAB portal
# Assign variables for the TIFF files being downloaded
central_bay_url = updated_urls["CentralBay"]
san_pablo_url = updated_urls["SanPabloBay"]
south_bay_url = updated_urls["SouthBay"]
# check URL being downloaded contains the correct date
print(central_bay_url)
print(san_pablo_url)
print(south_bay_url)
import requests
# Send a GET request to the URL
response = requests.get(central_bay_url)
# Check if the request was successful
if response.status_code == 200:
    # Define the local file path where the TIFF will be saved
    tiff_fp_central = os.path.join(full_path, 'CentralBay.tif')
    # Write the content to the file
    with open(tiff_fp_central, 'wb') as file:
        file.write(response.content)
    print(f"TIFF file downloaded and saved as {tiff_fp_central}")
else:
    print(f"Failed to download the TIFF file. HTTP Status code: {response.status_code}")
response = requests.get(san_pablo_url)

# Repeat for the other 2 files
if response.status_code == 200:
    # Define the local file path where the TIFF will be saved
    tiff_fp_sanpablo = os.path.join(full_path, 'SanPabloBay.tif')
    # Write the content to the file
    with open(tiff_fp_sanpablo, 'wb') as file:
        file.write(response.content)
    print(f"TIFF file downloaded and saved as {tiff_fp_sanpablo}")
else:
    print(f"Failed to download the TIFF file. HTTP Status code: {response.status_code}")

response = requests.get(south_bay_url)
if response.status_code == 200:
    # Define the local file path where the TIFF will be saved
    tiff_fp_south = os.path.join(full_path, 'SouthBay.tif')
    # Write the content to the file
    with open(tiff_fp_south, 'wb') as file:
        file.write(response.content)
    print(f"TIFF file downloaded and saved as {tiff_fp_south}")
else:
    print(f"Failed to download the TIFF file. HTTP Status code: {response.status_code}")
## Build attribute table for each input raster
try:
    arcpy.management.BuildRasterAttributeTable(tiff_fp_sanpablo)
    print("San Pablo Bay attribute table built.")
    arcpy.management.BuildRasterAttributeTable(tiff_fp_central)
    print("Central Bay attribute table built.")
    arcpy.management.BuildRasterAttributeTable(tiff_fp_south)
    print("South Bay attribute table built.")
except arcpy.ExecuteError:
    print("Error with ArcPy execution:")
    print(arcpy.GetMessages())
except Exception as e:
    print("Error has occurred:")
    print (e)
# create a new mosaic raster from 3 input rasters
# assign variable for output location
try:
    mosaic = os.path.join(full_path, 'mosaic.tif')
    arcpy.management.MosaicToNewRaster([tiff_fp_central, tiff_fp_sanpablo, tiff_fp_south], full_path,
                                       "mosaic.tif", "", "", "", "1", "", "")
    print("Mosaic to new raster complete")
except arcpy.ExecuteError:
    print("Error with ArcPy execution:")
    print(arcpy.GetMessages())
except Exception as e:
    print("An error has occurred:")
    print(e)

# make old mosaic file path with a nonsense date to be replaced with current date
old_mosaic = r"C:\Users\zombi\Documents\ArcGIS\Projects\GEOG562_Final_Project\TIFF_Files\2001_13_99\mosaic.tif"
new_mosaic = old_mosaic.replace("2001", year).replace("13", month).replace("99", day)
print(new_mosaic)

# Clean raster data values
# Make old raster file path with a nonsense date to be replaced with current date
old_cleanRaster = r"C:\Users\zombi\Documents\ArcGIS\Projects\GEOG562_Final_Project\OutRaster\2001_13_99_clean.tif"
new_cleanRaster = old_cleanRaster.replace("2001", year).replace("13", month).replace("99", day)
print(new_cleanRaster)
# Remove extraneous values from raster using reclassify tool
try:
    from arcpy.sa import *
    out_raster = arcpy.sa.Reclassify(in_raster=new_mosaic, reclass_field="Value",
    remap = "0 NODATA;251 NODATA;252 NODATA;253 NODATA;254 NODATA;255 NODATA",
    missing_values="DATA")
    out_raster.save(new_cleanRaster)
    print("Extraneous values removed from raster and saved to OutRaster folder.")
except arcpy.ExecuteError:
    print("Error with ArcPy execution:")
    print(arcpy.GetMessages(2))
except Exception as e:
    print("An error has occurred:")
    print(e)
## Compute change in values between most recent raster and previous raster
arcpy.CheckOutExtension("ImageAnalyst")
# Set date variables for previous day's raster
previous = today - timedelta(days=2)
previous_day = previous.strftime("%d")
previous_month = previous.strftime("%m")
previous_year = previous.strftime("%Y")
# Make old raster file path with a nonsense date to be replaced with previous day's date
oldRaster = r"C:\Users\zombi\Documents\ArcGIS\Projects\GEOG562_Final_Project\OutRaster\2001_13_99_clean.tif"
previous_cleanRaster = oldRaster.replace("2001", previous_year).replace("13", previous_month).replace("99", previous_day)
print("The previous day's raster is: " + str(previous_cleanRaster))
# Define input parameters
FromRaster = previous_cleanRaster
ToRaster = new_cleanRaster
ChangeType = "DIFFERENCE"
# Execute difference in values between today and previous day
print("Compute change raster will fail if a cleaned raster for previous day does not already exist.")
try:
    RasterDifference = arcpy.ia.ComputeChangeRaster(FromRaster, ToRaster, ChangeType, "", "", "CHANGED_PIXELS_ONLY")
    # Save output
    old_RasterDifference = r"C:\Users\zombi\Documents\ArcGIS\Projects\GEOG562_Final_Project\ChangeRaster\2001_13_99_change.tif"
    new_RasterDifference = old_RasterDifference.replace("2001", year).replace("13", month).replace("99", day)
    RasterDifference.save(new_RasterDifference)
    print(new_RasterDifference)
    print("Compute change in values complete and saved to ChangeRaster folder.")
except arcpy.ExecuteError:
    print("Error with ArcPy compute change execution:")
    print(arcpy.GetMessages())
except Exception as e:
    print("An error has occurred:")
    print(e)
## Map pixel values to chlorophyll-a values
# Convert cleaned raster to polygon
try:
    poly_base_path = r"C:\Users\zombi\Documents\ArcGIS\Projects\GEOG562_Final_Project\OutPolygons"
    file_name = yesterday.strftime('%Y_%m_%d' + "_poly")
    print(file_name)
    full_path = os.path.join(poly_base_path, file_name)
    print(full_path)
    #outpolygon = r"C:\Users\zombi\Documents\ArcGIS\Projects\GEOG562_Final_Project\outpolygon"
    arcpy.conversion.RasterToPolygon(new_cleanRaster, full_path)
    print("conversion complete")
except arcpy.ExecuteError:
    print("Error with ArcPy raster to polygon execution:")
    print(arcpy.GetMessages())
except Exception as e:
    print("An error has occurred:")
    print(e)
# Assign variable for csv file with replacement values
import csv
csv_file = r"C:\Users\zombi\Desktop\GEOG 562\Final Project\conversionchart.csv"
arcpy.env.overwriteOutput = True
# Add field Chlor to shapefile
arcpy.AddField_management(full_path, "Chlor", "DOUBLE")
# Create a dictionary from the CSV file
replacement_dict = {}
with open(csv_file, 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        attribute = row['attribute'].strip()
        new_value = row['new_value'].strip()
        replacement_dict[attribute] = new_value
# Check the contents of the replacement dictionary
print(f"Replacement dictionary: {replacement_dict}")
# Add values to Chlor field with an update cursor
with arcpy.da.UpdateCursor(full_path, ["gridcode", "Chlor"]) as cursor:
    for row in cursor:
        row[1] = row[0]
        old_value = str(row[0]).strip()
        if old_value in replacement_dict:
            new_value = replacement_dict[old_value]
            row[1] = new_value
            cursor.updateRow(row)
        else:
            print(f"No replacement found for '{old_value}'")
del cursor
# Calculate the total chlorophyll for the 3 bays for that day's data
summed_total = 0    # create a variable to add area values to
# use search cursor to find the concentration values
with arcpy.da.SearchCursor(full_path, "Chlor") as cursor_conc:
    for row in cursor_conc:
            summed_total = int(summed_total + row[0])    # add "Chlor" value for each row and iterate
print("The total chlorophyll for "+ str(yesterday.year) + "-" + str(yesterday.month) + "-" + str(yesterday.day) + " is " + str(summed_total))
