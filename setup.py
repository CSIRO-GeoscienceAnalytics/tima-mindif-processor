from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="tima-mindif",
    description="TIMA Min Dif Processor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version="1.5.5",
    packages=["tima"],
    maintainer="Samuel Bradley",
    maintainer_email="sam.bradley@csiro.au",
    python_requires=">=3.5, <4",
    entry_points={"console_scripts": ["tima-mindif=tima.__main__:main"]},
    install_requires=["pillow", "loguru", "numpy"],
    include_package_data=True,
    license="MIT",
    url="https://gitlab.com/csiro-geoanalytics/tima-utils/tima-mindif-processor",
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        # Indicate who your project is intended for
        "Intended Audience :: Science/Research",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: MIT License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
