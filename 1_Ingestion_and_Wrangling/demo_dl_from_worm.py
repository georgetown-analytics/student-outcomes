"""
Demo script to download files from an S3 Write Once Read Many (WORM) storage location in the cloud.

NOTE: You need a file on your local computer called ~/.aws/credentials with an access key and
secret-key. These can be gotten from your AWS account under the "Security Credentials." field 
when you click on your account name.

Structure of the ~/.aws/credentials file (3 lines):

[default]
aws_access_key_id = ACCESS_KEY 
aws_secret_access_key = SECRET_ACCESS_KEY 
"""

import boto3
conn = boto3.client('s3')


# Download a specific file
# conn.download_file('edu-data-bucket','grad_rate/acgr-sch-sy2018-19-long.csv','sy2018-19.csv')

# List all the objects (files) in the bucket
for key in conn.list_objects(Bucket='edu-data-bucket')['Contents']:
    print(key['Key'])
