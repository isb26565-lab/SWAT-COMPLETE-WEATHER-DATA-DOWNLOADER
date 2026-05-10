# SWAT Weather App - Windows Distribution

Goal: create a single Windows `.exe` that you can copy to other computers.

This project uses scientific/GIS libraries (`geopandas`, `rasterio`, `numpy`, `pandas`, `xarray`, `imdlib`, `shapely`, etc.). Packaging these into one executable is possible, but the build must be done on Windows and will produce a large output folder.

## 1) Build The EXE (on your build PC)

Open PowerShell in the project folder:

```powershell
cd C:\Users\shuja\Documents\Codex\2026-05-01\coding-utf-8-swat-complete-data
.\packaging\build_exe.ps1
```

Output will be created here:

```text
dist\SWAT_Weather_App\
```

## 1B) Build A Proper Windows Installer (Start Menu + Desktop + Startup)

This makes it behave like a normal desktop app.

1. Install Inno Setup on the build PC.
2. Build the PyInstaller bundle first (Step 1).
3. Compile the installer:

```powershell
iscc packaging\installer.iss
```

The installer will be created in:

```text
dist_installer\
SWAT_Weather_App_Setup.exe
```

Run the installer on any PC to get:
- Start Menu shortcut
- Optional Desktop icon
- Optional "Run at startup"

## 2) Copy To Another PC

Copy the whole folder:

```text
dist\SWAT_Weather_App\
```

On the other PC, run:

```text
SWAT_Weather_App.exe
```

## Notes / Requirements

- You still need the usual Windows prerequisites:
  - Microsoft Visual C++ Redistributable (often already installed).
- The app needs internet access to download NASA POWER + IMD data.
- IMD downloads are cached in the IMD raw folder you choose in the GUI.

## If The EXE Build Fails

Most failures come from missing Python packages on the build PC.

Recommended approach:
- Use the same Python environment you already run the downloader with (often Anaconda).
- Install missing packages in that environment.
- Re-run `.\packaging\build_exe.ps1`.
