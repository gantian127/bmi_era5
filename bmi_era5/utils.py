# -*- coding: utf-8 -*-
import xarray as xr
import cdsapi


class Era5Data:
    def __init__(self):
        self._data = None
        self._path = None
        self._request = None
        self._name = None

    @property
    def data(self):
        return self._data

    def get_data(self, name, request, path):
        c = cdsapi.Client()
        c.retrieve(name, request, path)

        self._data = xr.open_dataset(path, decode_cf=False)
        self._path = path
        self._name = name
        self._request = request

        return self.data

    def get_grid_info(self):
        # current implementation is for equal spacing 3 dim data (time, lat, lon).
        # needs update of BMI to support 4 or 5 dim data

        grid_info = {}

        if self._data:
            shape = [len(self._data.coords[coor]) for coor in ['number', 'level', 'latitude', 'longitude']
                     if coor in self._data.dims]  # [nz, ny, nx] order in bmi,

            y_spacing = round(self._data.coords['latitude'].values[0] - self._data.coords['latitude'].values[1], 3)
            x_spacing = round(self._data.coords['longitude'].values[1] - self._data.coords['longitude'].values[0], 3)

            y_lowerleft = self._data.coords['latitude'].values[-1]
            x_lowerleft = self._data.coords['longitude'].values[0]

            grid_info = {
                'shape': shape,
                'yx_spacing': (y_spacing, x_spacing),
                'yx_of_lower_left': (y_lowerleft, x_lowerleft),
            }

        return grid_info

    def get_time_info(self):
        time_info = {}

        # time values are float in BMI time function
        if self._data:
            time_info = {
                'start_time': float(self._data.time.values[0]),
                'time_step': 0.0 if len(self._data.time.values) == 1 else
                float(self._data.time.values[1] - self._data.time.values[0]),
                'end_time': float(self._data.time.values[-1]),
                'total_steps': len(self._data.time.values),
                'time_units': self._data.time.units,
                'calendar': self._data.time.calendar,
                'time_value': self._data.time.values.astype('float'),
            }

        return time_info

    def get_var_info(self):
        var_info = {}

        if self._data:
            for var_name in self._data.data_vars:
                var = self._data.data_vars[var_name]

                var_info[var.long_name] = {
                    'var_name': var_name,
                    'dtype': str(var.dtype),
                    'itemsize': var.values.itemsize,
                    'nbytes': var.values[0].nbytes,  # current time step nbytes
                    'units': var.units,
                    'location': 'node',
                }

        return var_info
