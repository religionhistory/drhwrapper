import setuptools

setuptools.setup(
    name="drhwrapper",
    version="0.1.1",
    description="A Python wrapper for the Database of Religious History API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/religionhistory/drhwrapper",
    author="Victor Møller Poulsen",
    author_email="victormoeller@gmail.com",
    license="Apache 2.0",
    project_urls={
        "Bug Tracker": "https://github.com/religionhistory/drhwrapper/issues",
        "Documentation": "https://github.com/religionhistory/drhwrapper#readme",
        "Source Code": "https://github.com/religionhistory/drhwrapper",
        "Demos": "https://github.com/religionhistory/drhwrapper/tree/main/demo",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",  # 4 - Beta
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "networkx>=3.0",
        "numpy>=1.24.0",
        "pandas>=2.0",
        "requests>=2.27.0",
        "tqdm",
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
    keywords=["religion", "history", "api", "wrapper"],
)
