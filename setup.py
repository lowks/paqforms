from setuptools import setup, find_packages


setup(
    name = 'PaqForms',
    version = '4.0.0.dev',
    license = 'Creative Commons Attribution-Noncommercial-Share Alike license',
    requires = ['markupsafe', 'babel', 'jinja2'],
    packages = find_packages(),
    include_package_data = True,
)
