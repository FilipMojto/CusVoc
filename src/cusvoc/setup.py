
from setuptools import setup, find_packages

setup(
    name='cusvoc',
    version='1.0',
    packages=find_packages(),  # Automatically finds and includes all packages and sub-packages
    py_modules=['cusvoc', 'language', 'vocabulary', 'audiopron', 'testvoc'],  # Specify individual modules if needed
    install_requires=[  # List of dependencies that will be installed automatically
        'prettytable',
        'argparse',
        'python-dotenv',
        'csv',
        # Add other dependencies as needed
    ],
    entry_points={
        'console_scripts': [
            'cusvoc = cusvoc:main',  # Automatically create a command-line executable for cusvoc.py
        ],
    },
    include_package_data=True,  # Include additional non-Python files (like .csv or .tsv) in the package
)