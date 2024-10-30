from __future__ import annotations

import os


def install_cds(config_path=""):
    # create configuration file
    url = "https://cds.climate.copernicus.eu/api"
    key = input("Enter Your CDS API Key: ")
    config_content = f"url: {url} \nkey: {key}"

    home_dir = os.path.expanduser("~")
    config_path = config_path if config_path else os.path.join(home_dir, ".cdsapirc")

    with open(config_path, "w") as config_file:
        config_file.write(config_content)

    print("CDS API Key file is created.")
