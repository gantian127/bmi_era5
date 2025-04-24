# bmi_era5
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10368878.svg)](https://doi.org/10.5281/zenodo.10368878)
[![Documentation Status](https://readthedocs.org/projects/bmi_era5/badge/?version=latest)](https://bmi-era5.readthedocs.io/en/latest/?badge=latest)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/gantian127/bmi_era5/blob/master/LICENSE.txt)

**Please note: Starting with release v0.2.0, the New CDS platform is now supported.**

bmi_era5 package is an implementation of the Basic Model Interface ([BMI](https://bmi-spec.readthedocs.io/en/latest/))
for the [ERA5](https://confluence.ecmwf.int/display/CKB/ERA5) dataset.
This package uses the [CDS API](https://cds.climate.copernicus.eu/how-to-api) to download
the ERA5 dataset and wraps the dataset with BMI for data control and query.
It currently supports 3-dimensional ERA5
datasets defined with dimensions such as valid_time (or date), latitude, and longitude.

This package is not implemented for people to use but is the key element to convert the ERA5 dataset into
a data component ([pymt_era5](https://pymt-era5.readthedocs.io/)) for
the [PyMT](https://pymt.readthedocs.io/en/latest/?badge=latest) modeling framework developed
by Community Surface Dynamics Modeling System ([CSDMS](https://csdms.colorado.edu/wiki/Main_Page)).

If you have any suggestion to improve the current function, please create a GitHub issue
[here](https://github.com/gantian127/bmi_era5/issues).


### Install package

#### Stable Release

The bmi_era5 package and its dependencies can be installed with pip
```
$ pip install bmi_era5
```

or conda
```
$ conda install -c conda-forge bmi_era5
```

#### From Source

After downloading the source code, run the following command from top-level folder
to install bmi_era5.
```
$ pip install -e .
```

### Citation
Please include the following references when citing this software package:

Gan, T., Tucker, G.E., Hutton, E.W.H., Piper, M.D., Overeem, I., Kettner, A.J.,
Campforts, B., Moriarty, J.M., Undzis, B., Pierce, E., McCready, L., 2024:
CSDMS Data Components: data–model integration tools for Earth surface processes
modeling. Geosci. Model Dev., 17, 2165–2185. https://doi.org/10.5194/gmd-17-2165-2024

Gan, T. (2024). CSDMS ERA5 Data Component. Zenodo. https://doi.org/10.5281/zenodo.10368878


### Quick Start
Below shows how to use two methods to download the ERA5 datasets.

You can learn more details from the [tutorial notebook](https://github.com/gantian127/bmi_era5/blob/master/notebooks/bmi_era5.ipynb).
To run this notebook, please go to the [CSDMS EKT Lab](https://csdms.colorado.edu/wiki/Lab-0018) and follow the instruction in the "Lab notes" section.

#### Example 1: use CDS API to download the ERA5 data

```python
import cdsapi
import xarray
import matplotlib.pyplot as plt

c = cdsapi.Client()

c.retrieve(
    "reanalysis-era5-single-levels",
    {
        "product_type": "reanalysis",
        "format": "netcdf",
        "variable": ["2m_temperature"],
        "year": "2021",
        "month": "01",
        "day": "01",
        "time": ["00:00", "01:00", "02:00"],
        "area": [41, -109, 36, -102],
        "grid": [0.25, 0.25],
    },
    "download.nc",
)

# load netCDF data
dataset = xarray.open_dataset("download.nc")

# select 2 meter temperature on 2021-01-01 at 00:00
air_temp = dataset.t2m.isel(valid_time=0)

# plot data
air_temp.plot(figsize=(9, 5))
plt.title("2 metre temperature in Colorado on Jan 1st, 2021 at 00:00")
```
![tif_plot](docs/source/_static/tif_plot.png)


#### Example 2: use BmiEra5 class to download the ERA5 data (Demonstration of how to use BMI)

```python
from bmi_era5 import BmiEra5
import numpy as np
import matplotlib.pyplot as plt

data_comp = BmiEra5()
data_comp.initialize("config_file.yaml")

# get variable info
var_name = data_comp.get_output_var_names()[0]
var_unit = data_comp.get_var_units(var_name)
var_location = data_comp.get_var_location(var_name)
var_type = data_comp.get_var_type(var_name)
var_grid = data_comp.get_var_grid(var_name)
var_itemsize = data_comp.get_var_itemsize(var_name)
var_nbytes = data_comp.get_var_nbytes(var_name)

print(f"{var_name=}")
print(f"{var_unit=}")
print(f"{var_location=}")
print(f"{var_type=}")
print(f"{var_grid=}")
print(f"{var_itemsize=}")
print(f"{var_nbytes=}")

# get time info
start_time = data_comp.get_start_time()
end_time = data_comp.get_end_time()
time_step = data_comp.get_time_step()
time_unit = data_comp.get_time_units()
time_steps = int((end_time - start_time) / time_step) + 1

print(f"{start_time=}")
print(f"{end_time=}")
print(f"{time_step=}")
print(f"{time_unit=}")
print(f"{time_steps=}")

# get variable grid info
grid_rank = data_comp.get_grid_rank(var_grid)
grid_size = data_comp.get_grid_size(var_grid)

grid_shape = np.empty(grid_rank, int)
data_comp.get_grid_shape(var_grid, grid_shape)

grid_spacing = np.empty(grid_rank)
data_comp.get_grid_spacing(var_grid, grid_spacing)

grid_origin = np.empty(grid_rank)
data_comp.get_grid_origin(var_grid, grid_origin)

print(f"{grid_rank=}")
print(f"{grid_size=}")
print(f"{grid_shape=}")
print(f"{grid_spacing=}")
print(f"{grid_origin=}")

# get variable data
data = np.empty(grid_size, var_type)
data_comp.get_value("2 metre temperature", data)
data_2D = data.reshape(grid_shape)

# get X, Y extent for plot
min_y, min_x = grid_origin
max_y = min_y + grid_spacing[0] * (grid_shape[0] - 1)
max_x = min_x + grid_spacing[1] * (grid_shape[1] - 1)
dy = grid_spacing[0] / 2
dx = grid_spacing[1] / 2
extent = [min_x - dx, max_x + dx, min_y - dy, max_y + dy]

# plot data
fig, ax = plt.subplots(1, 1, figsize=(9, 5))
im = ax.imshow(data_2D, extent=extent)
cbar = fig.colorbar(im)
cbar.set_label("2 metre temperature [K]")
plt.xlabel("longitude [degree_east]")
plt.ylabel("latitude [degree_north]")
plt.title("2 metre temperature in Colorado on Jan 1st, 2021 at 00:00")

# finalize the data component
data_comp.finalize()
```

![tif_plot](docs/source/_static/tif_plot.png)
