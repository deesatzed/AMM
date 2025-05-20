#!/usr/bin/env python
# Minimal setup.py for conda environments

from setuptools import setup, find_packages

setup(
    name="agno-memory-module",
    version="0.1.0",
    packages=find_packages(include=['agno*']),
    package_data={
        'agno': ['templates/*', 'static/*'],
    },
    # Skip install_requires since we're using conda
    install_requires=[],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'amm-gui=agno.gui.app:main',
            'amm-mcp=agno.mcp.server:main',
            'amm-key-manager=agno.cli.key_manager.__main__:main',
        ],
    },
    # Add any additional package data needed
    include_package_data=True,
)
