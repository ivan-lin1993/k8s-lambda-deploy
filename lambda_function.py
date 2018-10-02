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
    try:
        s3 = boto3.resource('s3')
        s3.Object(os.environ['S3_BUCKET'], os.environ['KUBECONFIG_FILE']).download_file('/tmp/kubeconfig')
    except Exception as e:
        print(e)
        raise
    return '/tmp/kubeconfig'


def load_deploy_config():
    try:
        s3 = boto3.resource('s3')
        res = json.loads(s3.Object(os.environ['S3_BUCKET'], os.environ['DEPLOY_CONFIG']).get()['Body'].read().decode())
    except Exception as e:
        print(e)
        raise
    return res


def setting_kubefile():
    fileurl = download_kubeconfig()
    k8s.config.load_kube_config(fileurl)
    

def main():
    setting_kubefile()
    delploy_config = load_deploy_config()
    deployfile = delploy_config['deployment_file']
    client = k8s.client.CoreApi()


if __name__ == '__main__':
    main()
