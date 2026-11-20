import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'mision_autonoma'
setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'maps'), glob('maps/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Juan David',
    maintainer_email='juangidd@outlook.es',
    description='Misiones autonomas Nav2',
    license='Apache-2.0',
    entry_points={'console_scripts': ['mission_node = mision_autonoma.mission_node:main']},
)
