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

session = None
bucker_manager = None

@click.group()
@click.option('--profile', default = None, help = "Use a AWS profile")
def cli(profile):
    """Webotron deploys website to AWS."""
    session_cfg = {}
    if profile:
        sesison_cfg['profile_name'] = profile
    global session, bucket_manager
    session = boto3.Session(**session_cfg)
    bucket_manager = BucketManager(session)
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
