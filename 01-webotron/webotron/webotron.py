# coding: utf-8
#!/usr/bin/python
""" Webotron: Deploy websites with AWS.
    Webtron automates the process of piublishing static websites to s3 froms scratch"""

import boto3
import click
import mimetypes
from botocore.exceptions import ClientError
from pathlib import Path

print("Note: By default all the resources will be created in us-east-2 region")

session = boto3.Session(profile_name = 'PythonAutomation')
s3 = session.resource('s3')

@click.group()
def cli():
    """Webotron deploys website to AWS."""
    pass


@cli.command('list_buckets')
def list_buckets():
    """List all."""
    print("Following are the list of buckets from S3 with: ")
    for bucket in s3.buckets.all():
        print(bucket)


@cli.command('list_bucket_obj')
@click.argument('bucket')
def list_bucket_obj(bucket):
    """List objects in a s3 bucket."""
    print('Objects inside the %(buck)s bucket are: '%{'buck':bucket})
    for obj in s3.Bucket(bucket).objects.all():
        print(obj)


@cli.command('setup_bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    """Create a bucket."""
    s3_bucket = None
    try:
        s3_bucket = s3.create_bucket(Bucket=bucket,
            CreateBucketConfiguration = {'LocationConstraint':'us-east-2'}
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print('Bucket %s is already owned by you ' % bucket )
            print('Proceeding further with the bucket %s' % bucket)
            s3_bucket = s3.Bucket(bucket)

        else:
            raise e

    """Adding public policy to the bucket."""
    policy = """
       {
         "Version":"2012-10-17",
         "Statement":[
           {
             "Sid":"AddPerm",
             "Effect":"Allow",
             "Principal": "*",
             "Action":["s3:GetObject"],
             "Resource":["arn:aws:s3:::%s/*"]
           }
         ]
       }
       """ % s3_bucket.name
    policy = policy.strip()
    buc_pol = s3_bucket.Policy()
    buc_pol.put(Policy = policy)

    "Performing website hosting"
    ws = s3_bucket.Website()
    ws.put(WebsiteConfiguration = {
    'ErrorDocument':{
        'Key':'error.html'
        },
    'IndexDocument':{
        'Suffix':'index.html'
      }}
      )
    return

def upload_file(s3_bucket, path, key):
    content_tye = mimetypes.guess_type(key)[0] or 'text/plain'
    s3_bucket.upload_file(
        path,
        key,
        ExtraArgs={
            'ContentType' : content_type
        })


@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket')
def sync(pathname, bucket):
    """Sync contents of Pathname to Bucket."""
    root = Path(pathname).expanduser().resolve()
    s3_bucket = s3.Bucket(bucket)
    def handle_directory(target):
        for p in target.iterdir():
            if p.is_dir(): handle_directory(p)
            if p.is_file(): upload_file(s3_bucket,str(p), str(p.relative_to(root)))

    handle_directory(root)

if __name__ == '__main__':
    cli()
