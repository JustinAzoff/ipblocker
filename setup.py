from setuptools import setup, find_packages
import sys, os
from glob import glob

version = '0.8.8'

setup(name='ipblocker',
    version=version,
    description="IP Blocker",
    long_description="""\
""",
    classifiers=["Topic :: System :: Networking", "Topic :: Security", "Topic :: System :: Networking :: Firewalls"],
    keywords='ip block null route',
    author='Justin Azoff',
    author_email='JAzoff@uamail.albany.edu',
    url='',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "SQLAlchemy >= 0.8, <=1.0",
        "WebHelpers",
        "IPy",
        # -*- Extra requirements: -*-
    ],
    extras_require = {
        'blockers':  ["httplib2","cif","pygeoip"],
    },
    entry_points= {
        'paste.app_install': [
            'main   = paste.script.appinstall:Installer',
        ],
        'console_scripts': [
            'ipblocker-block-spamhaus     = ipblocker.block_spamhaus:main',
            'ipblocker-block-zeustracker  = ipblocker.block_zeustracker:main',
            'ipblocker-block-snort        = ipblocker.block_snort:main',
            'ipblocker-block-cif          = ipblocker.block_cif:main',
        ]
    },
    test_suite='nose.collector',
    scripts=glob('scripts/*'),
    )
