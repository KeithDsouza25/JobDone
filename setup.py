from setuptools import setup, find_packages

setup(
    name="jobdone",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if not line.startswith("#")
    ],
) 