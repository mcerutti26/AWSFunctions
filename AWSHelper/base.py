import os
import boto3
from botocore.exceptions import ClientError
import json
import pymysql
from pypika import Table, MySQLQuery


def get_aws_secret(secret_name, region_name):
    # Create an AWS Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e
    secret = get_secret_value_response['SecretString']
    return secret


def get_aws_parameter(param_name):
    botoclient = boto3.client('ssm')
    response = botoclient.get_parameter(
        Name=param_name,
        WithDecryption=True
    )
    return response['Parameter']['Value']


class AWSDataBase:
    # Initialize the AWSDataBase class attributes including endpoints, usernames, and passwords.
    def __init__(self, slack_id):
        secret = json.loads(get_aws_secret(secret_name=os.environ['dbSecretName'], region_name=os.environ['awsRegion']))
        self.endpoint = secret['host']
        self.username = secret['username']
        self.password = secret['password']
        self.database_name = 'LGUploads'
        self.slack_id = slack_id
        self._cur_user_data = None
        self._db_user_id = None
        self._active_strain_reservations = None
        self._active_plasmid_reservations = None
        self._db_username = None

    # Define a context manager with enter and exit functions When used in later code with a "with" statement,
    # __enter__ can open the database connection and return the object for use within the with block, and __exit__
    # can then be responsible for closing the database connection - regardless of whether an error occurred within
    # the with block.
    def __enter__(self):
        self.connection = pymysql.connect(host=self.endpoint, user=self.username, passwd=self.password,
                                          db=self.database_name)
        self.cursor = self.connection.cursor()
        self.dict_cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.connection.close()
        return exc_type is None

    # Query all user data within the Users table of the database for the specified slack_id. This info is then
    # referenced by other functions for retrieval of specific attributes.
    @property
    def cur_user_data(self):
        if self._cur_user_data is None:
            users = Table('Users')
            execution_sql = MySQLQuery.from_(users).select('*').where(users.slack_id == self.slack_id)
            self.dict_cursor.execute(execution_sql.get_sql())
            self._cur_user_data = self.dict_cursor.fetchall()
        return self._cur_user_data

    @property
    def db_user_id(self):
        if self._db_user_id is None:
            self._db_user_id = self.cur_user_data[0]['user_id']
        return self._db_user_id

    @property
    def db_username(self):
        if self._db_username is None:
            self._db_username = self.cur_user_data[0]['user_name']
        return self._db_username

    @property
    def token(self):
        return self.cur_user_data[0]['LGToken']

    @token.setter
    def token(self, value):
        users = Table('Users')
        execution_sql = MySQLQuery.update(users).set('LGToken', value).where(users.user_id == self.db_user_id)
        self.cursor.execute(execution_sql.get_sql())
        self.connection.commit()
