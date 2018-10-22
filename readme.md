# EKS lambda deployment
From this [project](https://github.com/ivan-lin1993/eks-codedeploy-demo)

## Require
Using Lambda python version 3.6

## Create lambda role
- AWS S3 read
- AWS EKS full access
- Pipeline full access (PutJobResult)

## Install dependency
```
$ ./install.sh
```
## Zip it
```
$ zip -r lambda_function.zip ./
```

## Upload to lambda

### Setting Env
- CLUSTER_NAME
- API_ENDPOINT : EKS api endpoint
- DEPLOYFILE_NAME  ( ex: eks-deployment.yml )
- S3_BUCKET

## Contributor
- [KYPan](https://github.com/KYPan0818)