#%%
import logging
import boto3
from botocore.exceptions import ClientError
import os


def create_presigned_url(method, object_name, expiration=3600):


    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')
    bucket_name = os.environ['SP_APP_BUCKET']
    try:
        response = s3_client.generate_presigned_url(method,
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response

def get(path):
    return create_presigned_url('get_object', path, expiration=3600*24*5)

def put(path):
    return create_presigned_url('put_object', path, expiration=3600*24*5)

get('/uploads/shared/lib_drumroll')
put('/uploads/shared/lib_drumroll')
