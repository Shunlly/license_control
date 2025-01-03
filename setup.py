from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="license_control",
    version="0.0.3",
    author="chenshuhang",
    author_email="a330289953@gmail.com",
    description="A comprehensive license management module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Shunlly/license_control",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
    install_requires=[
        "cryptography>=3.4.7",
    ],
    keywords="license control, licensing",
)