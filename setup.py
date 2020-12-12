from setuptools import setup

setup(
    name="rpi-jenkins-tower-light",
    version="2.0.2",
    author="Bram Driesen",
    author_email="bram.opensource@gmail.com",
    description="Python script for a Jenkins tower light to visualise the status using Raspberry Pi",
    url="https://github.com/BramDriesen/rpi-jenkins-tower-light",
    packages=['rpi-jenkins-tower-light'],
    install_requires=['jenkinsapi'],
)
