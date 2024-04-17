from setuptools import setup

setup(
    name='AWSFunctions',
    version='1.0.4',
    packages=['AWSHelper','SlackHelper'],
    url='',
    license='',
    author='Mark Cerutti',
    author_email='mark.cerutti@grobio.com',
    description='Retrieve information from AWS securely.',
    include_package_data=True,
    install_requires=['boto3', 'botocore', 'pymysql', 'pypika', 'slack_sdk']
)
