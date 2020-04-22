from setuptools import setup, find_packages


setup(
    name='mturk-tools',
    version='0.0.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': 'mtools-cli = mtools.cli:cli'
    },
    install_requires=[
        'boto3>=1.0.0',
        'click>=7.1.1',
        'sqlalchemy>=1.3.16',
    ],
)
