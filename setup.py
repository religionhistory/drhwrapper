import setuptools

setuptools.setup(
    name="drhwrapper",
    version="0.1.0",
    description="A Python wrapper for the Database of Religious History API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/religionhistory/drhwrapper",
    author="Victor Møller Poulsen",
    author_email="victormoeller@gmail.com",
    licence="Apache 2.0",
    project_urls={
        "https://github.com/religionhistory/drhwrapper/issues"
        # add example documentation maybe when we know where it lives
    },
    classifiers={
        "Development Status :: 3 - Alpha",  # 4 - Beta
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        # check compatibility
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    },
    python_requires=">=3.8",  # also check this (has to be accurate)
    install_requires=[""],  # dependencies (packages)
    packages=setuptools.find_packages(),  # ?
    include_package_data=True,
    keywords=["religion", "history", "api", "wrapper"],
)
