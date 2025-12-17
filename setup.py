from setuptools import setup, find_packages

setup(
    name='regional_dashboard',
    version='0.0.5',
    description='Regional Dashboard',
    author='SurgiShop',
    author_email='gary.starr@surgishop.com',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=['frappe']
)
