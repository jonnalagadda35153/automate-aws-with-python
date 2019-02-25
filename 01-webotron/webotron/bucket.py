#!/usr/bin
# -*- coding: utf-8 -*-
from botocore.exceptions import ClientError
import boto3
import mimetypes
from pathlib import Path
from botocore.exceptions import ClientError

class BucketManager:
    """Manages as S3 Buckets."""

    def __init__(self, session):
        """Creates a BucketManager Object."""
        self.s3 = session.resource('s3')


    def all_buckets(self):
        """Returns all buckets of an account."""
        return self.s3.buckets.all()


    def all_objects(self,bucket):
        """Returns all objects inside a bucket"""
        return self.s3.Bucket(bucket).objects.all()


    def init_bucket(self,bucket_name):
        """Creates a bucket/ if exists throws error"""
        s3_bucket = None
        try:
            s3_bucket = self.s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration = {
                    'LocationConstraint':'us-east-2'
                }
            )
        except ClientError as error:
            if error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                print('Bucket %s is already owned by you ' % bucket_name )
                print('Proceeding further with the bucket %s' % bucket_name)
                s3_bucket = self.s3.Bucket(bucket_name)
            else:
                raise error

        return s3_bucket

    def set_policy(self,bucket):
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
           """ % bucket.name
        policy = policy.strip()
        buc_pol = bucket.Policy()
        buc_pol.put(Policy = policy)

    def configure_website(self,bucket):
        "Performing website hosting"
        ws = bucket.Website()
        ws.put(WebsiteConfiguration = {
        'ErrorDocument':{
            'Key':'error.html'
            },
        'IndexDocument':{
            'Suffix':'index.html'
          }}
          )

    @staticmethod
    def upload_file(bucket, path, key):
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'
        return bucket.upload_file(
            path,
            key,
            ExtraArgs={
                'ContentType' : content_type
            })

    def sync(self, pathname, bucket_name):
        bucket = self.s3.Bucket(bucket_name)
        root = Path(pathname).expanduser().resolve()
        def handle_directory(target):
            for p in target.iterdir():
                if p.is_dir(): handle_directory(p)
                if p.is_file(): self.upload_file(bucket,str(p), str(p.relative_to(root)))

        handle_directory(root)
