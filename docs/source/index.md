```{image} _static/bmi_era5_logo.png
:align: center
:alt: bmi_era5
:scale: 22%
:target: https://bmi-era5.readthedocs.io/en/latest/
```

[bmi_era5 package][bmi_era5-github] is an implementation of
the [Basic Model Interface (BMI)][bmi-docs] for the [ERA5][ERA5] dataset.
This package uses the [CDS API][cds-api] to download the ERA5 dataset and wraps the
dataset with BMI for data control and query. It currently supports 3-dimensional ERA5
datasets defined with dimensions as [valid_time, latitude, longitude].

This package is not implemented for people to use but is the key element to convert the ERA5 dataset into
a data component ([pymt_era5][pymt_era5]) for the [PyMT][pymt-docs]
modeling framework developed by Community Surface Dynamics Modeling System
([CSDMS][csdms]).


# Installation

**Stable Release**

The bmi_era5 package and its dependencies can be installed with either *pip* or *conda*,

````{tab} pip
```console
pip install bmi_era5
```
````

````{tab} conda
```console
conda install -c conda-forge bmi_era5
```
````

**From Source**

After downloading the source code, run the following command from top-level folder
to install bmi_era5.

```console
pip install -e .
```

# Quick Start

Below shows how to use two methods to download the ERA5 datasets.

You can learn more details from the [tutorial notebook][bmi_era5-notebook].
To run this notebook, please go to the [CSDMS EKT Lab][bmi_era5-csdms] and follow
the instruction in the "Lab notes" section.

**Example 1**: use CDS API to download the ERA5 data.

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
        "variable": ["2m_temperature", "total_precipitation"],
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

# select 2 metre temperature on 2021-01-01 at 00:00
air_temp = dataset.t2m.isel(valid_time=0)

# plot data
air_temp.plot(figsize=(9, 5))
plt.title("2 metre temperature in Colorado on Jan 1st, 2021 at 00:00")
```

```{image} _static/tif_plot.png
```

**Example 2**: use BmiEra5 class to download the ERA5 data (Demonstration of how to use BMI).

```python
from bmi_era5 import BmiEra5
import numpy as np
import matplotlib.pyplot as plt

data_comp = BmiEra5()
data_comp.initialize("config_file.yaml")

# get variable info
for var_name in data_comp.get_output_var_names():
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

<!-- links -->
[bmi-docs]: https://bmi.readthedocs.io
[csdms]: https://csdms.colorado.edu
[pymt-docs]: https://pymt.readthedocs.io
[cds-api]: https://cds.climate.copernicus.eu/how-to-api
[bmi_era5-github]: https://github.com/gantian127/bmi_era5/
[ERA5]: https://confluence.ecmwf.int/display/CKB/ERA5
[bmi_era5-notebook]: https://github.com/gantian127/bmi_era5/blob/master/notebooks/bmi_era5.ipynb
[bmi_era5-csdms]: https://csdms.colorado.edu/wiki/Lab-0018
[pymt_era5]: https://pymt-era5.readthedocs.io/
