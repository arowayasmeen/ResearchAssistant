from setuptools import setup, find_packages

setup(
    name="research-assistant",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "flask",
        "flask-cors",
        "requests",
        "scikit-learn",
        "sentence_transformers",
        "python-dotenv",
        "google-search-results",
    ],
    entry_points={
        "console_scripts": [
            "research-assistant=research_assistant.cli:main",
        ],
    },
)