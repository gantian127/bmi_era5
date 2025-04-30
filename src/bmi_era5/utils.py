from __future__ import annotations

import os
import zipfile

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
        # check file format
        file_path, ext = os.path.splitext(path)

        if ext not in [".nc", ".zip"]:
            raise ValueError(
                "Please provide a valid path with '.nc' or '.zip' file extension."
            )

        # download file if not exists
        if not os.path.exists(path):
            c = cdsapi.Client()
            c.retrieve(name, request, path)

        # check file format and load data
        with open(path, "rb") as f:  # Read the first 4 bytes
            header = f.read(4)
        if header.startswith(b"CDF") or header.startswith(b"\x89HDF"):  # netcdf
            nc_path = file_path + ".nc"
            os.rename(path, nc_path)
            self._data = xr.open_dataset(nc_path, decode_cf=False)
            self._path = nc_path
        elif header.startswith(b"PK\x03\x04"):  # zip file
            zip_path = file_path + ".zip"
            os.rename(path, zip_path)
            os.makedirs(file_path, exist_ok=True)
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(file_path)
            data_list = [
                xr.open_dataset(os.path.join(file_path, sub_file))
                for sub_file in os.listdir(file_path)
                if ".nc" in sub_file
            ]
            try:
                self._data = xr.merge(data_list)
            except Exception:
                print(f"Failed to load the dataset from {file_path}")

            self._path = zip_path
        else:
            raise TypeError("The dataset is saved in an unsupported file format.")

        self._name = name
        self._request = request
        print(f"The dataset is saved in {self._path}")

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
        time_var = None

        # time values are float in BMI time function
        if self._data:
            for time_var_name in ["valid_time", "date"]:
                if time_var_name in self._data.keys():
                    time_var = self._data[time_var_name]
                    break

            if time_var is not None:
                if "units" in time_var.attrs and "calendar" in time_var.attrs:
                    # time_var follows CF convention values
                    time_info = {
                        "start_time": float(time_var.values[0]),
                        "time_step": 0.0
                        if len(time_var.values) == 1
                        else float(time_var.values[1] - time_var.values[0]),
                        "end_time": float(time_var.values[-1]),
                        "total_steps": len(time_var.values),
                        "time_units": time_var.units,
                        "calendar": time_var.calendar,
                        "time_value": time_var.values.astype("float"),
                    }
                else:
                    # convert date time to CF convention values
                    date_objs = time_var.values.astype("datetime64[s]").astype("O")
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
