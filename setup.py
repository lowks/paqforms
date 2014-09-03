from setuptools import setup, find_packages


setup(
    name = 'paqforms',
    version = '4.5',
    license = 'MIT',
    requires = ['markupsafe', 'babel', 'jinja2'],
    packages = find_packages(),
    include_package_data = True,
)
