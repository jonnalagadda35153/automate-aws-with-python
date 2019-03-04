#!/usr/bin/python
# -*- coding: utf-8 -*-
from botocore.exceptions import ClientError
import boto3
import mimetypes
import util
import pprint
from hashlib import md5
from pathlib import Path
from functools import reduce
from botocore.exceptions import ClientError

class BucketManager:
    """Manage as S3 Buckets."""

    CHUNK_SIZE = 8388608

    def __init__(self, session):
        """Create a BucketManager Object."""
        self.session = session
        self.s3 = session.resource('s3')
        self.transfer_config = boto3.s3.transfer.TransferConfig(
            multipart_chunksize = self.CHUNK_SIZE,
            multipart_threshold = self.CHUNK_SIZE
        )
        self.manifest = {}


    def get_region_name(self,bucket):
        """Get the region of the bucket."""
        bucket_location = self.s3.meta.client.get_bucket_location(Bucket = bucket.name)

        return bucket_location["LocationConstraint"] or 'us-east-1'

    def get_bucket_url(self, bucket):
        """Get the bucket URL for this bucket."""
        return "http://{}.{}".format(bucket.name, util.get_endpoint(self.get_region_name(bucket)).host)

    def all_buckets(self):
        """Return all buckets of an account."""
        return self.s3.buckets.all()

    def all_objects(self,bucket):
        """Return all objects inside a bucket."""
        return self.s3.Bucket(bucket).objects.all()

    def init_bucket(self,bucket_name):
        """Create a bucket/ if exists throws error."""
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
        """Perform website hosting."""
        ws = bucket.Website()
        ws.put(WebsiteConfiguration = {
        'ErrorDocument':{
            'Key':'error.html'
            },
        'IndexDocument':{
            'Suffix':'index.html'
          }}
          )

    def load_manifest(self,bucket):
        """Load manifest to upload only updated file since last commit."""
        paginator = self.s3.meta.client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket = bucket.name):
            for obj in page.get('Contents',[]):
                self.manifest[obj['Key']] = obj ['ETag']

    @staticmethod
    def hash_data(data):
        """To generate a hash value for a data component."""
        hash = md5()
        hash.update(data)
        return hash

    def gen_etag(self, path):
        """Generate local e-tag to compare with the e-tag in bucket."""
        hashes = []

        with open(path, 'rb') as f:
            while True:
                data = f.read(self.CHUNK_SIZE)

                if not data:
                    break
                hashes.append(self.hash_data(data))

            if not hashes:
                return
            elif len(hashes) == 1:
                return '"{}"'.format(hashes[0].hexdigest())
            else:
                hash = self.hash_data(reduce(lambda x, y: x+y, (h.digest() for h in hashes)))
                return '"{}-{}"'.format(hash.hexdigest(), len(hashes))

    #@staticmethod
    def upload_file(self, bucket, path, key):
        """Uplod file to S3 bucket_manager."""
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'
        etag = self.gen_etag(path)

        if self.manifest.get(key,' ') == etag:
            print("Skipping {}, eatags match".format(key))
            return

        return bucket.upload_file(
            path,
            key,
            ExtraArgs={
                'ContentType' : content_type
            },
            Config = self.transfer_config)

    def sync(self, pathname, bucket_name):
        """Sync contents in local machine to that in s3 bucket."""
        bucket = self.s3.Bucket(bucket_name)
        self.load_manifest(bucket)
        root = Path(pathname).expanduser().resolve()
        def handle_directory(target):
            for p in target.iterdir():
                if p.is_dir(): handle_directory(p)
                if p.is_file():
                    self.upload_file(bucket, str(p), str(p.relative_to(root)))
                    print("Uploaded the file {}".format(p.name))
        handle_directory(root)
