from xml.etree.ElementTree import VERSION
from setuptools import setup, find_packages
from typing import List


# Variable declaring for set up function
PROJECT_NAME = "Adult Census Income Prediction"
VERSION = "0.0.2"
DESCRIPTION = "This Project For ineuron Internship Portal End To End."
AUTHOR = "Vivek Mishra"
PACKAGE = ['AC_income_prediction']
REQUIREMENT_FILE_NAME = "requirements.txt"

def get_requirement_details()->List[str]:
    """
    Description: This function is going to return list of requirement 
    mention in requirements.txt file
    return This function is going to return a list which contain name 
    of libraries mentioned in requirements.txt file
    
    """
    with open(REQUIREMENT_FILE_NAME) as requiremet_file:
        return requiremet_file.readlines().remove('-e .')
    

setup(
    name=PROJECT_NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    packages=find_packages(),
    install_requries=get_requirement_details())