from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="xml-inspector",
    version="1.0.0",
    author="",
    author_email="",
    description="A quality assurance tool for XML files that validates configuration settings against standardized requirements",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/xml-inspector",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Text Processing :: Markup :: XML",
    ],
    python_requires=">=3.8",
    install_requires=[
        "lxml>=4.9.0",
        "PyYAML>=6.0",
        "click>=8.0.0",
        "colorama>=0.4.0",
        "jinja2>=3.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "types-PyYAML",
        ],
    },
    entry_points={
        "console_scripts": [
            "xml-inspector=xml_inspector.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)