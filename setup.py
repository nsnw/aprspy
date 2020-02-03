import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aprspy",
    version="0.3.1",
    author="Andy Smith",
    author_email="andy@nsnw.ca",
    description="An APRS parser for Python",
    long_description=long_description,
    url="https://github.com/nsnw/aprspy",
    packages=setuptools.find_packages(),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "geopy"
    ],
    python_requires='>=3.7',
)
