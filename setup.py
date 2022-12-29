from setuptools import setup, find_packages

package_name = 'dps'

required_packages = [
    'numpy',
    'opencv-python-headless',
    'pyautogui',
    'pyyaml',
]

setup(
    name=package_name,
    version='0.0.1',
    python_requires='>=3.7.0',
    install_requires=required_packages,
    packages=find_packages(),
    zip_safe=True,
    maintainer='Gleb Siroki',
    maintainer_email='foo@bar.com',
    description='DIY photo scanner',
)
