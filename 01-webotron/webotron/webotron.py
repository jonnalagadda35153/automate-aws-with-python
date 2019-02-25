#!/usr/bin/python
# coding: utf-8

""" Webotron: Deploy websites with AWS.
    Webtron automates the process of deploying and publishing static websites to s3 froms scratch
    We can create -> configure and set them up for static webste hosting
    We can also configure DNS and CDN and SSL with AWS cloud front
    """

import boto3
import click
import mimetypes
from bucket import BucketManager



print("Note: By default all the resources will be created in us-east-2 region")

session = boto3.Session(profile_name = 'PythonAutomation')
bucket_manager = BucketManager(session)
#s3 = session.resource('s3')

@click.group()
def cli():
    """Webotron deploys website to AWS."""
    pass


@cli.command('list_buckets')
def list_buckets():
    """List all."""
    print("Following are the list of buckets from S3 with: ")
    for bucket in bucket_manager.all_buckets():
        print(bucket)


@cli.command('list_bucket_obj')
@click.argument('bucket')
def list_bucket_obj(bucket):
    """List objects in a s3 bucket."""
    print('Objects inside the %(buck)s bucket are: '%{'buck':bucket})
    for obj in bucket_manager.all_objects(bucket):
        print(obj)


@cli.command('setup_bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    """Create a bucket."""
    s3_bucket = bucket_manager.init_bucket(bucket)
    bucker_manager.set_policy(s3_bucket)
    bucket_manager.configure_website(s3_bucket)
    return

@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket')
def sync(pathname, bucket):
    """Sync contents of Pathname to Bucket."""
    #s3_bucket = s3.Bucket(bucket)
    bucket_manager.sync(pathname,bucket)



if __name__ == '__main__':
    cli()
