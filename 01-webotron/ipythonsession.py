# coding: utf-8
import boto3
session = boto3.Session(profile_name = 'PythonAutomation')
s3 = session.resource('s3')
