from __future__ import annotations

import os.path
from datetime import datetime

import cdsapi
import cftime
import numpy as np
import xarray as xr


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
        if not os.path.exists(path):
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
            shape = [
                len(self._data.coords[coor])
                for coor in ["number", "level", "latitude", "longitude"]
                if coor in self._data.dims
            ]  # [nz, ny, nx] order in bmi,

            if (
                len(self._data.coords["latitude"].values) > 1
                and len(self._data.coords["longitude"].values) > 1
            ):
                y_spacing = round(
                    self._data.coords["latitude"].values[0]
                    - self._data.coords["latitude"].values[1],
                    3,
                )
                x_spacing = round(
                    self._data.coords["longitude"].values[1]
                    - self._data.coords["longitude"].values[0],
                    3,
                )
            elif "grid" in self._request.keys():
                y_spacing = self._request["grid"][1]
                x_spacing = self._request["grid"][0]
            else:
                raise Exception(
                    "The configuration file needs to specify the "
                    '"grid" info in the "request" parameter.'
                )

            y_lowerleft = self._data.coords["latitude"].values[-1]
            x_lowerleft = self._data.coords["longitude"].values[0]

            grid_info = {
                "shape": shape,
                "yx_spacing": (y_spacing, x_spacing),
                "yx_of_lower_left": (y_lowerleft, x_lowerleft),
            }

        return grid_info

    def get_time_info(self):
        time_info = {}

        # time values are float in BMI time function
        if self._data:
            if "valid_time" in self._data.keys():
                time_info = {
                    "start_time": float(self._data.valid_time.values[0]),
                    "time_step": 0.0
                    if len(self._data.valid_time.values) == 1
                    else float(
                        self._data.valid_time.values[1]
                        - self._data.valid_time.values[0]
                    ),
                    "end_time": float(self._data.valid_time.values[-1]),
                    "total_steps": len(self._data.valid_time.values),
                    "time_units": self._data.valid_time.units,
                    "calendar": self._data.valid_time.calendar,
                    "time_value": self._data.valid_time.values.astype("float"),
                }
            elif "date" in self._data.keys():
                # convert date time to CF convention values
                date_objs = [
                    datetime.strptime(str(date_value), "%Y%m%d")
                    for date_value in self._data.date.values
                ]
                time_units = "seconds since 1970-01-01"
                calendar = "proleptic_gregorian"
                cf_dates = cftime.date2num(
                    date_objs, units=time_units, calendar=calendar
                )

                time_info = {
                    "start_time": float(cf_dates[0]),
                    "time_step": 0.0
                    if len(cf_dates) == 1
                    else float(cf_dates[1] - cf_dates[0]),
                    "end_time": float(cf_dates[-1]),
                    "total_steps": len(cf_dates),
                    "time_units": time_units,
                    "calendar": calendar,
                    "time_value": np.array(cf_dates, dtype=float),
                }

        return time_info

    def get_var_info(self):
        var_info = {}

        if self._data:
            for var_name in self._data.data_vars:
                var = self._data.data_vars[var_name]
                if var.ndim >= 3:
                    var_info[var.long_name] = {
                        "var_name": var_name,
                        "dtype": type(var.scale_factor).__name__
                        if "scale_factor" in var.attrs.keys()
                        else str(var.dtype),
                        "itemsize": var.values.itemsize,
                        "nbytes": var.values[0].nbytes,  # current time step nbytes
                        "units": var.units,
                        "location": "node",
                    }

        return var_info
