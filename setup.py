from setuptools import setup, find_packages
with open("requirements.txt") as f:
    requir = f.read().splitlines()
    
setup(
    name="ClaraMed",
    author="Emit B0i",
    author_email="sahootanmay2005@gmail.com",
    packages=find_packages(),
    install_requires=requir
)