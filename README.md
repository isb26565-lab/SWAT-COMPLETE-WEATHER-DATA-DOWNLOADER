# SWAT Complete Weather Data Downloader

![SWAT Modeling](https://img.shields.io/badge/SWAT-Modeling-success) ![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![License](https://img.shields.io/badge/License-MIT-green)

A professional, automated toolkit for downloading, processing, and formatting real observed weather datasets specifically tailored for the **Soil and Water Assessment Tool (SWAT)**. 

This tool drastically reduces the time required for hydrological modeling preparation by fully automating the extraction of meteorological data and generating SWAT-ready formatted `.txt` files.

## 🌟 Key Features

* **Dual Interface**: Includes both a user-friendly Graphical User Interface (GUI) app and a robust Command Line script for advanced batch processing.
* **IMD Data Integration**: Automatically fetches and processes high-resolution grid data for Rainfall and Temperature from the Indian Meteorological Department (IMD), applying watershed area weighting.
* **NASA POWER Integration**: Automatically retrieves accurate Solar Radiation, Wind Speed, and Relative Humidity data.
* **Spatial Processing**: Built-in support for Shapefiles (`.shp`) to clip and process data precisely for your study area/watershed using `geopandas` and `rasterio`.
* **SWAT-Ready Output**: Automatically generates the specifically formatted `.txt` files required by SWAT (pcp, tmp, slr, hmd, wnd) along with their corresponding station location files.
* **Missing Data Handling**: Intelligent interpolation and handling of missing data points (-99.0) to ensure smooth SWAT execution.

## 🚀 Getting Started

### Prerequisites

You will need Python installed on your system. It is highly recommended to use a virtual environment. Install the required dependencies using:

```bash
pip install -r requirements.txt
```

*(Core dependencies include: `imdlib`, `xarray`, `netcdf4`, `pandas`, `geopandas`, `requests`, `scipy`, `rasterio`, `rioxarray`)*

### Usage

**1. Using the Desktop Application (GUI)**
For a user-friendly experience, run the included batch file or Python script:
```bash
python swat_weather_app.py
```
This will launch a modern interface where you can input your coordinates, select date ranges, and generate your data with a few clicks.

**2. Using the Command Line Script**
For advanced users or automated pipelines, edit the USER CONFIGURATION section in the main script and run:
```bash
python swat_complete_data_downloader_real.py
```

## 📂 Project Structure
* `swat_weather_app.py`: The main Graphical User Interface for the application.
* `swat_complete_data_downloader_real.py`: The core engine script handling the heavy lifting of data retrieval and spatial processing.
* `Run_SWAT_Weather_App.bat`: A quick-launch shortcut for Windows users.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page if you want to contribute.

## 📝 License
This project is open-source and available under the [MIT License](LICENSE).
