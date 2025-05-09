from setuptools import setup, find_packages

setup(
    name="forest_app",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "pydantic",
        "pytest",
        "pytest-asyncio",
    ],
) 