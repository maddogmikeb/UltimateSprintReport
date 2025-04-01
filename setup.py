from setuptools import setup, find_packages

setup(
    name="UltimateJiraSprintReport",
    version="0.1.0",
    author="Your Name",
    author_email="mike@7ft10.com",
    description="A project to generate sprint reports from Jira data.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/maddogmikeb/UltimateSprintReport",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "atlassian-python-api",
        "matplotlib",
        "numpy",
        "pandas",
        "tqdm",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)