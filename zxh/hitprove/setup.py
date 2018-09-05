from setuptools import setup

setup(
    name = 'hit',
    version = '0.1.0',
    packages = ['prove'],
    entry_points = {
        'console_scripts': [
            'hit = prove.__main__:main'
        ]
    })
