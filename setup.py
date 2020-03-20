import setuptools
import codecs

with codecs.open("README.md", "r", 'utf_8_sig') as fh:
    long_description = fh.read()

setuptools.setup(
    name="minter-sdk",
    version="1.0.22",
    author="U-node Team",
    author_email="rymka1989@gmail.com",
    description=u"Python SDK for Minter Network",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/U-node/minter-sdk",
    packages=setuptools.find_packages(include=['mintersdk']),
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        'rlp',
        'bitcoin',
        'mnemonic',
        'base58',
        'pysha3',
        'requests',
        'pyqrcode',
        'deprecated'
    ]
)
