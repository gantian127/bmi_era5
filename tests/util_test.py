from __future__ import annotations

import os

import xarray

from bmi_era5 import Era5Data

parameters = [('reanalysis-era5-single-levels',
               'single_hour.nc',
               {'product_type': 'reanalysis',
                'variable': ['2m_temperature', 'total_precipitation'],
                'year': '2021',
                'month': '01',
                'day': '01',
                'time': ['00:00', '01:00', '02:00'],
                'format': 'netcdf',
                'area': [41, -109, 36, -102],
                'grid': [0.25, 0.25]}
               )]


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

    assert grid_info_2['shape'] == [21, 29]
    assert grid_info_2['yx_spacing'] == (0.25, 0.25)
    assert grid_info_2['yx_of_lower_left'] == (36.0, -109.0)


@pytest.mark.parametrize("name, file, era5_req", parameters)
def test_get_var_info(tmpdir, name, file, era5_req):
    path = os.path.join(tmpdir, file)

    era5 = Era5Data()
    var_info_1 = era5.get_grid_info()

    assert var_info_1 == {}

    era5.get_data(name, era5_req, path)
    var_info_2 = era5.get_var_info()
    assert len(var_info_2) == 2
    assert 'Total precipitation' in var_info_2.keys()
    assert '2 metre temperature' in var_info_2.keys()

    var = var_info_2['Total precipitation']
    assert var['var_name'] == 'tp'
    assert var['dtype'] == 'float64'
    assert var['itemsize'] == 2
    assert var['nbytes'] == 1218
    assert var['units'] == 'm'
    assert var['location'] == 'node'


@pytest.mark.parametrize("name, file, era5_req", parameters)
def test_get_time_info(tmpdir, name, file, era5_req):
    path = os.path.join(tmpdir, file)

    era5 = Era5Data()
    time_info_1 = era5.get_time_info()

    assert time_info_1 == {}

    era5.get_data(name, era5_req, path)
    time_info_2 = era5.get_time_info()

    assert time_info_2['start_time'] == 1060680
    assert time_info_2['end_time'] == 1060682
    assert time_info_2['time_step'] == 1
    assert time_info_2['total_steps'] == 3
    assert time_info_2['time_units'] == 'hours since 1900-01-01 00:00:00.0'
    assert time_info_2['calendar'] == 'gregorian'
