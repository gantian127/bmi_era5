from __future__ import annotations

import os

import pytest
import xarray
from bmi_era5 import Era5Data

parameters = [
    (
        "reanalysis-era5-single-levels",
        "single_hour.nc",
        {
            "product_type": "reanalysis",
            "variable": ["2m_temperature", "total_precipitation"],
            "year": "2021",
            "month": "01",
            "day": "01",
            "time": ["00:00", "01:00", "02:00"],
            "format": "netcdf",
            "area": [41, -109, 36, -102],
            "grid": [0.25, 0.25],
        },
    )
]

parameters2 = [
    (
        "reanalysis-era5-single-levels-monthly-means",
        "monthly_mean.nc",
        {
            "product_type": ["monthly_averaged_reanalysis"],
            "variable": ["2m_dewpoint_temperature"],
            "year": ["2022"],
            "month": ["01", "02", "03", "04"],
            "time": ["00:00"],
            "data_format": "netcdf",
            "download_format": "unarchived",
            "area": [39, -106, 36, -103],
        },
    )
]


@pytest.mark.parametrize("name, file, era5_req", parameters)
def test_get_data(tmpdir, name, file, era5_req):
    path = os.path.join(tmpdir, file)
    data = Era5Data().get_data(name, era5_req, path)

    assert isinstance(data, xarray.core.dataset.Dataset)
    assert len(os.listdir(tmpdir)) == 1


@pytest.mark.parametrize("name, file, era5_req", parameters)
def test_get_grid_info(tmpdir, name, file, era5_req):
    path = os.path.join(tmpdir, file)

    era5 = Era5Data()
    grid_info_1 = era5.get_grid_info()

    assert grid_info_1 == {}

    era5.get_data(name, era5_req, path)
    grid_info_2 = era5.get_grid_info()

    assert grid_info_2["shape"] == [21, 29]
    assert grid_info_2["yx_spacing"] == (0.25, 0.25)
    assert grid_info_2["yx_of_lower_left"] == (36.0, -109.0)


@pytest.mark.parametrize("name, file, era5_req", parameters)
def test_get_var_info(tmpdir, name, file, era5_req):
    path = os.path.join(tmpdir, file)

    era5 = Era5Data()
    var_info_1 = era5.get_grid_info()

    assert var_info_1 == {}

    era5.get_data(name, era5_req, path)
    var_info_2 = era5.get_var_info()

    assert "Total precipitation" in var_info_2.keys()
    assert "2 metre temperature" in var_info_2.keys()

    var = var_info_2["Total precipitation"]
    assert var["var_name"] == "tp"
    assert var["dtype"] == "float32"
    assert var["itemsize"] == 4
    assert var["nbytes"] == 2436
    assert var["units"] == "m"
    assert var["location"] == "node"


@pytest.mark.parametrize("name, file, era5_req", parameters)
def test_get_time_info_valid_time(tmpdir, name, file, era5_req):
    """Test when time variable is valid_time"""
    path = os.path.join(tmpdir, file)

    era5 = Era5Data()
    time_info_1 = era5.get_time_info()

    assert time_info_1 == {}

    era5.get_data(name, era5_req, path)
    time_info_2 = era5.get_time_info()

    assert time_info_2["start_time"] == 1609459200.0
    assert time_info_2["end_time"] == 1609466400.0
    assert time_info_2["time_step"] == 3600.0
    assert time_info_2["total_steps"] == 3
    assert time_info_2["time_units"] == "seconds since 1970-01-01"
    assert time_info_2["calendar"] == "proleptic_gregorian"


@pytest.mark.parametrize("name, file, era5_req", parameters2)
def test_get_time_info_date(tmpdir, name, file, era5_req):
    """Test when time variable is date"""

    path = os.path.join(tmpdir, file)

    era5 = Era5Data()
    time_info_1 = era5.get_time_info()

    assert time_info_1 == {}

    era5.get_data(name, era5_req, path)
    time_info_2 = era5.get_time_info()

    assert time_info_2["start_time"] == 1640995200.0
    assert time_info_2["end_time"] == 1648771200.0
    assert time_info_2["time_step"] == 2678400.0
    assert time_info_2["total_steps"] == 4
    assert time_info_2["time_units"] == "seconds since 1970-01-01"
    assert time_info_2["calendar"] == "proleptic_gregorian"
