# mtcadapters package build script

from setuptools import setup, find_packages
import mtcadapter

setup(
    name='mtcadapters',
    version=mtcadapter.__version__,
    description='Python library implementing MTConnect adapters',
    url='https://github.com/Demo-Smart-Factory-Concordia-University/MTCAdapters',
    author=mtcadapter.__author__,
    author_email=mtcadapter.__email__,
    license='BSD 3-Clause License',
    packages=find_packages(),
    install_requires=['psutil',
                      'requests',
                      'dotenv'],
)
