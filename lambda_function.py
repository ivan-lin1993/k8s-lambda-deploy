import json
import boto3
import kubernetes as k8s
import os
import yaml
import subprocess


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
        s3.Object(os.environ['S3_BUCKET'],os.environ['CLUSTER_NAME'] + '/kubeconfig' ).download_file('/tmp/kubeconfig')
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
    

def get_token(cluster_name):
    args = ("./aws-iam-authenticator", "token", "-i", cluster_name)
    popen = subprocess.Popen(args, stdout=subprocess.PIPE)
    popen.wait()
    res = popen.stdout.read().rstrip()
    res = json.loads(res)
    print(res['status']['token'])
    return res['status']['token']


def k8s_auth_setting():
    api_token = get_token(os.environ['CLUSTER_NAME'])
    configuration = k8s.client.Configuration()
    configuration.host = os.environ['API_ENDPOINT']
    configuration.verify_ssl = False
    configuration.debug = True
    configuration.api_key['authorization'] = "Bearer " + api_token
    configuration.assert_hostname = True
    configuration.verify_ssl = False
    k8s.client.Configuration.set_default(configuration)


def main():
    #setting_kubefile()
    k8s_auth_setting()
    delploy_file = load_deploy_yml()
    v1 = k8s.client.ExtensionsV1beta1Api()
    deploy_yml = yaml.load(delploy_file)
    print("========================================================")
    print(deploy_yml)
    print("=======================================================")
    resp = v1.patch_namespaced_deployment(name='eks-web', body=deploy_yml, namespace="default")
    
    #resp = v1.create_namespaced_deployment( namespace="default", body= deploy_yml)
    print("Deployment created. status='%s'" % str(resp.status))


if __name__ == '__main__':
    main()
