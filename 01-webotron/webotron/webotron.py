# coding: utf-8
import boto3
from botocore.exceptions import ClientError
import click
print("Note: By default all the resources will be created in us-east-2 region")
session = boto3.Session(profile_name = 'PythonAutomation')
s3 = session.resource('s3')

@click.group()
def cli():
    "Webotron deploys website to AWS"
    pass

@cli.command('list_buckets')
def list_buckets():
    "List all buckcets"
    print("Following are the list of buckets from S3 with: ")
    for bucket in s3.buckets.all():
        print(bucket)

@cli.command('list_bucket_obj')
@click.argument('bucket')
def list_bucket_obj(bucket):
    "List objects in a s3 bucket"
    print('Objects inside the %(buck)s bucket are: '%{'buck':bucket})
    for obj in s3.Bucket(bucket).objects.all():
        print(obj)

@cli.command('setup_bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    "Creating a bucket"
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

    "Adding public policy to the bucket"
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

if __name__ == '__main__':
    cli()
