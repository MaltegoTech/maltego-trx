from setuptools import setup

setup(name='maltego-trx',
      version='0.1',
      description='Python library used to develop Maltego transforms',
      url='https://github.com/paterva/maltego-trx/',
      author='Paterva Staff',
      author_email='technical@paterva.com',
      license='MIT',
      packages=[
          'maltego_trx',
          'maltego_trx/template_dir',
          'maltego_trx/template_dir/transforms'
      ],
      entry_points={'console_scripts': [
          'maltego-trx = maltego_trx.commands:execute_from_command_line',
      ]},
      zip_safe=False
      )
