from setuptools import find_packages, setup

import versioneer

with open("requirements.txt", "rt") as fp:
    install_requires = [
        line for line in fp.read().splitlines()
        if line and not line.startswith("#")
    ]

setup(
        name="stock_manager",
        version=versioneer.get_version(),
        cmdclass=versioneer.get_cmdclass(),
        license="BSD",
        author="SLAC National Accelerator Laboratory",
        packages=find_packages(),
        include_package_data=True,
        description="SLAC LCLS Stock Management Application",
        long_description=open("README.md").read(),
        long_description_content_type="text/markdown",
        install_requires=install_requires,
        entry_points={
            'gui_scripts': ['stock_manager=stock_manager.__main__:main'],
            'console_scripts': ['stock_manager=stock_manager.__main__:main']
        },
        python_requires='>=3.10',
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: BSD License",
        ],
)
