import subprocess
import os


def install_cds(config_path=''):
    # create configuration file
    url = 'https://cds.climate.copernicus.eu/api/v2'
    key = input('Enter Your CDS API Key: ')
    config_content = 'url: {} \nkey: {}'.format(url, key)

    home_dir = os.path.expanduser('~')
    config_path = config_path if config_path else os.path.join(home_dir, '.cdsapirc')

    with open(config_path, 'w') as config_file:
        config_file.write(config_content)

    print('CDS API Key file is created.')

    # # install cdsapi
    # install = subprocess.run(["pip", "install", "cdsapi"], check=True)
    # if install.returncode == 0:
    #     print('cdsapi package is successfully installed.')
