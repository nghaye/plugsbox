from setuptools import find_packages, setup

setup(
    name='plugsbox',
    version='0.1.0',
    description='A NetBox plugin for managing campus network outlets.',
    author='Votre Nom',
    author_email='votre.email@example.com',
    license='Apache 2.0',
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)

