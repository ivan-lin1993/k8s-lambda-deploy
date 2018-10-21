import json
import boto3
import kubernetes as k8s
import os
import yaml
import subprocess

code_pipeline = boto3.client('codepipeline')
job_id = None

def lambda_handler(event, context):
    # TODO implement
    print("========Lambda Start.========")
    main(event)
    return {
        "statusCode": 200,
        "body": json.dumps('Lambda end.')
    }

def download_kubeconfig():
    try:
        s3 = boto3.resource('s3')
        s3.Object(os.environ['S3_BUCKET'],os.environ['CLUSTER_NAME'] + '/kubeconfig' ).download_file('/tmp/kubeconfig')
    except Exception as e:
        print(e)
        put_job_failure(job_id, 'Function exception: ' + str(e))
        raise
    return '/tmp/kubeconfig'

def load_deploy_config():
    try:
        s3 = boto3.resource('s3')
        res = json.loads(s3.Object(os.environ['S3_BUCKET'], os.environ['CLUSTER_NAME'] + '/' + os.environ['DEPLOY_CONFIG']).get()['Body'].read().decode())
    except Exception as e:
        print(e)
        put_job_failure(job_id, 'Function exception: ' + str(e))
        raise
    return res

def load_deploy_yml():
    print("### Loading deploy yaml.")
    try:
        s3 = boto3.resource('s3')
        res = s3.Object(os.environ['S3_BUCKET'], os.environ['CLUSTER_NAME'] + '/' + os.environ['DEPLOYFILE_NAME']).get()['Body'].read().decode()
    except Exception as e:
        print(e)
        put_job_failure(job_id, 'Function exception: ' + str(e))
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
    print("### Setting k8s cluster auth.")
    api_token = get_token(os.environ['CLUSTER_NAME'])
    configuration = k8s.client.Configuration()
    configuration.host = os.environ['API_ENDPOINT']
    configuration.verify_ssl = False
    configuration.debug = True
    configuration.api_key['authorization'] = "Bearer " + api_token
    configuration.assert_hostname = True
    configuration.verify_ssl = False
    k8s.client.Configuration.set_default(configuration)

def put_job_success(job, message):
    print('### Putting job success.')
    print(message)
    code_pipeline.put_job_success_result(jobId=job)

def put_job_failure(job, message):
    print('### Putting job failure.')
    print(message)
    code_pipeline.put_job_failure_result(jobId=job, failureDetails={'message': message, 'type': 'JobFailed'})

def main(event):
    
    job_id = event['CodePipeline.job']['id']
    
    try:
        #setting_kubefile()
        k8s_auth_setting()
        delploy_file = load_deploy_yml()
        v1 = k8s.client.ExtensionsV1beta1Api()
    except Exception as e:
        print("========================")
        print('Function failed due to exception.') 
        print(e)
        put_job_failure(job_id, 'Function exception: ' + str(e))

    deploy_yml = yaml.load(delploy_file)
    print("\n### Deploy file:")
    print("========================")
    print(deploy_yml)
    print("========================")
    print("### Deploy to EKS cluster.")
    
    try:
        resp = v1.patch_namespaced_deployment(name='eks-web', body=deploy_yml, namespace="default")
        #resp = v1.create_namespaced_deployment( namespace="default", body= deploy_yml)
        print("\n### Deployment created. status='%s'" % str(resp.status))
        put_job_success(job_id, ("Deployment created."))
    except Exception as e:
        print('### Function failed due to exception.') 
        print(e)
        put_job_failure(job_id, 'Function exception: ' + str(e))
