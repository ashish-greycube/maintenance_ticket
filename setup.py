from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in maintenance_ticket/__init__.py
from maintenance_ticket import __version__ as version

setup(
	name="maintenance_ticket",
	version=version,
	description="customization for asante maintenance ticket",
	author="GreyCube Technologies",
	author_email="admin@greycube.in",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
