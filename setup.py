from setuptools import setup
from maltego_trx import VERSION

setup(
    name='maltego-trx',
    version=VERSION,
    description='Python library used to develop Maltego transforms',
    url='https://github.com/paterva/maltego-trx/',
    author='Maltego Staff',
    author_email='support@maltego.com',
    license='MIT',
    install_requires=[
        'flask>=1',
        'six>=1',
        'cryptography==3.3.2'  # pinned for now as newer versions require setuptools_rust
    ],
    packages=[
        'maltego_trx',
        'maltego_trx/template_dir',
        'maltego_trx/template_dir/transforms'
    ],
    entry_points={
        'console_scripts': [
            'maltego-trx = maltego_trx.commands:execute_from_command_line',
        ]
    },
    zip_safe=False
)
