import json
from dependency import boto3
from dependency import kubernetes as k8s
import os

def lambda_handler(event, context):
    # TODO implement
    return {
        "statusCode": 200,
        "body": json.dumps('Hello from Lambda!')
    }

def download_kubeconfig():
    s3 = boto3.resource('s3')
    s3.Object(os.environ['S3_BUCKET'], os.environ['KUBECONFIG_FILE']).download_file('/tmp/kubeconfig')



def setting_kubefile():
    fileurl = download_kubeconfig()

    k8s.config.load_kube_config(fileurl)