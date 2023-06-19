import setuptools

with open("README.md", "r", encoding = 'utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="kult",
    version="0.1.1a1",
    author="lewisleedev",
    author_email="lewislee@lewislee.net",
    description="경희대학교 도서관 비공식 파이썬 라이브러리",
    url="https://github.com/lewisleedev/kult",
    packages=setuptools.find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "requests",
    ],
    python_requires='>=3.6',
)