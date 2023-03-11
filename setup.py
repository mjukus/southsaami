from setuptools import find_packages, setup

setup(
    name="flaskr",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask",
        "flask-ckeditor",
        "WTForms",  # Other ckeditor doesn't work, even though it isn't used.
    ],
)