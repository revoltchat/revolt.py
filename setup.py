import pathlib

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="revolt.py",
    version="0.0.1",
    description="Python wrapper around revolt.chat",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Zomatree/revolt.py",
    author="Zomatree",
    classifiers=[
        "Development Status :: 3 - Alpha",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: MIT License",

        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],

    keywords="wrapper, async, api, websockets, http",
    packages=find_packages(),
    python_requires=">=3.9",
    extras_require={
        "speedups": ["ujson", "aiohttp[speedups]==3.7.4.post0", "msgpack==1.0.2"],
    },
    project_urls={
        "Bug Reports": "https://github.com/Zomatree/revolt.py/issues",
        "Source": "https://github.com/Zomatree/revolt.py/",
    },
)
