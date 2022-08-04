import setuptools


with open('requirements.txt', 'r') as req:
    required_packages = req.read().splitlines()


setuptools.setup(
    name='sharethis',
    version='0.0.1',
    author='Gaweł Dydycz',
    author_email='gdydycz@edu.cdv.pl',
    description='Sharethis.',
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    include_package_data=True,
    install_requires=required_packages,
    python_requires='>=3.10',
)
