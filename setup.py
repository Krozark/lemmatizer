import setuptools

from lemmatizer import (
    __version__,
)

setuptools.setup(
    name="lemmatizer",
    version=__version__,
    description="An lib that wrap a lemma dict as a python mapping",
    author="Maxime Barbier",
    author_email="maxime.barbier1991+lemmatizer@gmail.com",
    url="https://github.com/Krozark/lemmatizer",
    keywords="lemmatizer",
    packages=setuptools.find_packages(),
    package_data={"lemmatizer" : ["data/*.txt",]},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
