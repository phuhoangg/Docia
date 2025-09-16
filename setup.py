"""
Docia CLI Package Setup
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="docia-cli",
    version="1.0.0",
    author="Docia Team",
    author_email="team@docia.ai",
    description="VisionLM-powered Document Intelligence CLI Tool",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/phuhoangg/docia",
    packages=find_packages(include=['docia*', 'cli*']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "docia=cli.app:docia",
        ],
    },
    include_package_data=True,
    package_data={
        "docia": ["*.md", "*.txt", "*.template"],
    },
    project_urls={
        "Bug Reports": "https://github.com/phuhoangg/docia/issues",
        "Source": "https://github.com/phuhoangg/docia"
    },
)