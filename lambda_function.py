import json
import boto3
import kubernetes as k8s
import os
import yaml


def lambda_handler(event, context):
    # TODO implement
    main()
    return {
        "statusCode": 200,
        "body": json.dumps('Hello from Lambda!')
    }

def download_kubeconfig():
    try:
        s3 = boto3.resource('s3')
        s3.Object(os.environ['S3_BUCKET'],os.environ['CLUSTER_NAME'] + '/' + os.environ['KUBECONFIG_FILE']).download_file('/tmp/kubeconfig')
    except Exception as e:
        print(e)
        raise
    return '/tmp/kubeconfig'





def load_deploy_config():
    try:
        s3 = boto3.resource('s3')
        res = json.loads(s3.Object(os.environ['S3_BUCKET'], os.environ['CLUSTER_NAME'] + '/' + os.environ['DEPLOY_CONFIG']).get()['Body'].read().decode())
    except Exception as e:
        print(e)
        raise
    return res


def load_deploy_yml():
    try:
        s3 = boto3.resource('s3')
        res = s3.Object(os.environ['S3_BUCKET'], os.environ['CLUSTER_NAME'] + '/' + os.environ['DEPLOYFILE']).get()['Body'].read().decode()
    except Exception as e:
        print(e)
        raise
    return res



def setting_kubefile():
    fileurl = download_kubeconfig()
    k8s.config.load_kube_config(fileurl)
    

def main():
    setting_kubefile()
    delploy_file = load_deploy_yml()
    client = k8s.client.CoreApi()
    delploy_yml = yaml.load(delploy_file)
    k8s_beta = k8s.client.ExtensionsV1beta1Api()
    resp = k8s_beta.create_namespaced_deployment(
        body=delploy_yml, namespace="default")
    print("Deployment created. status='%s'" % str(resp.status))


if __name__ == '__main__':
    main()
