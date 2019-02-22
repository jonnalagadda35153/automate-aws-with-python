# coding: utf-8
import boto3
import click
session = boto3.Session(profile_name = 'PythonAutomation')
s3 = session.resource('s3')

#print("Following are the list of buckets from S3: ")
@click.group()
def cli():
    "Webotron deploys website to AWS"
    pass

@cli.command('list_buckets')
def list_buckets():
    "List all buckcets"
    for bucket in s3.buckets.all():
        print(bucket)

@cli.command('list_bucket_obj')
@click.argument('bucket')
def list_bucket_obj(bucket):
    "List objects in a s3 bucket"
    for obj in s3.Bucket(bucket).objects.all():
        print(obj)

if __name__ == '__main__':
    cli()
