from setuptools import setup, find_packages

setup(
    name="migraine-tracker",
    version="0.1.0",
    description="A Flask web application to track and analyze migraine patterns",
    author="Vincent Perricone",
    author_email="vhp@fastmail.fm",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "flask>=2.0.0",
        "flask-sqlalchemy>=3.0.0",
        "flask-wtf>=1.0.0",
        "sqlalchemy>=1.4.0",
        "python-dateutil>=2.8.0",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "migraine-tracker=app:app",
        ],
    },
)
