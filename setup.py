from setuptools import setup, find_packages
from simfin_tools.simfin_tools import __version__

setup(
    name="simfin-tools",
    version=__version__,
    description="A command line tool to retrieve financial data using simfin",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="Hiroshi Ogawa",
    author_email="",  # Add your email if you want
    url="https://github.com/HiroshiOkada/simfin-tools-cli",
    packages=find_packages(),
    install_requires=[
        "simfin",
        "pandas",
        "python-dotenv",
    ],
    entry_points={
        'console_scripts': [
            'sfin=simfin_tools.simfin_tools.cli:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.6",
)