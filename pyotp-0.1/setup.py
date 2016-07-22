try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Python OTP library',
    'author': 'Buzz',
    'url': 'URL to get it at.',
    'download_url': 'Where to download it.',
    'author_email': 'davudbuzz@gmail.com',
    'version': '0.1',
    'install_requires': [],
    'packages': ['pyotp'],
    'scripts': [],
    'name': 'pyotp'
}

setup(**config)
