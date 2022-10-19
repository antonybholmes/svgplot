import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="svgplot",
    version="1.0.0",
    author="Antony Holmes",
    author_email="antony@antonyholmes.com",
    description="A library for creating plots directly onto an SVG canvas.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/antonybholmes/svgplot",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
