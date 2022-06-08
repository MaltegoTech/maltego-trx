from setuptools import setup
from maltego_trx import VERSION

with open("README.md", "r") as readme_md:
    long_description = readme_md.read()

setup(
    name='maltego-trx',
    version=VERSION,
    description='Python library used to develop Maltego transforms',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/paterva/maltego-trx/',
    author='Maltego Staff',
    author_email='support@maltego.com',
    license='MIT',
    install_requires=[
        'flask>=1',
        'six>=1',
        'cryptography==3.3.2'  # pinned for now as newer versions require setuptools_rust
    ],
    extras_require={
        ':python_version == "3.6"': [
            'dataclasses',
        ],
    },
    packages=[
        'maltego_trx',
        'maltego_trx/template_dir',
        'maltego_trx/template_dir/transforms'
    ],
    package_data={
        'maltego_trx/template_dir': [
            'settings.csv',
            'transforms.csv',
            'docker-compose.yml',
            'Dockerfile',
            'requirements.txt',
        ]
    },
    entry_points={
        'console_scripts': [
            'maltego-trx = maltego_trx.commands:execute_from_command_line',
        ]
    },
    zip_safe=False
)
