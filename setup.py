#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from email_profile import __version__
from setuptools import setup
from setuptools.command.install import install


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


class CustomInstallCommand(install):
    def run(self):
        install.run(self)


setup(
    name="email-profile",
    fullname='email-profile',
    version=__version__,
    author="Fernando Celmer",
    author_email="email@fernandocelmer.com",
    description="📩 Email Profile",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls = {
        'Homepage': 'https://github.com/linux-profile/email-profile',
        'Repository': 'https://github.com/linux-profile/email-profile',
        'Documentation': 'https://github.com/linux-profile/email-profile/blob/master/README.md',
        'Issues': 'https://github.com/linux-profile/email-profile/issues',
    },
    cmdclass={
        'install': CustomInstallCommand,
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    packages=['email_profile'],
    include_package_data=True,
    python_requires=">=3.8",
    zip_safe=True,
    entry_points={
        'console_scripts': ['email=email_profile.main:main'],
    },
)
