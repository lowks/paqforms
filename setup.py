from setuptools import setup, find_packages


setup(
    name = 'PaqForms',
    version = '4.5',
    license = 'BSD',
    requires = ['markupsafe', 'babel', 'jinja2'],
    packages = find_packages(),
    include_package_data = True,
)
