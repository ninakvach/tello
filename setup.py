## ! DO NOT MANUALLY INVOKE THIS setup.py, USE CATKIN INSTEADfrom
from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup
#fetch values from package.xml
setup_args = generate_distutils_setup(packages=['​tello​'],package_dir={'': 'include'},)
setup(**setup_args)
