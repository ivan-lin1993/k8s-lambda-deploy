# EKS lambda deployment

## Create lambda role
- AWS S3 read
- AWS EKS full access


## Install dependency
```
$ ./install.sh
```
## Zip it
```
$ zip -r lambda_function.zip ./
```

## Upload to lambda

### Role
- S3 full access
- EKS full access

### Setting Env
- CLUSTER_NAME
- API_ENDPOINT : EKS api endpoint
- DEPLOYFILE_NAME  ( ex: eks-deployment.yml )
- S3_BUCKET

