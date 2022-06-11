# aws-eks-private

CloudFormation Templates and Scripts to deploy EKS in a Private Only VPC

# Overview

This repository aims to include resources and supporting scripts and documentation to deploy and maintain an AWS EKS Cluster deployed in a Private Network only.

The current status of this project is still in early development.

## AWS Components

![AWS Components](implementation-diagram-aws-components.png)

## EKS Components

![EKS Components](implementation-diagram-eks-components.png)

# Preparation and Pre-requisites

The following must be available on your system:

* Python 3.8.13 or later
* AWS CLI 2.7.7 or later 
* Git version 2.36.1 or later

_**Note**_: Older version of the software may work, but the versions above was used during the development and is therefore known to work

All command examples will assume a Unix like operating system with either BASH or ZSH as the shell. Windows users should consider using WSL with the latest Ubuntu distribution.

In addition you must obvisouly also have access to AWS. If you do not yet have an account, head over to [AWS and create a free account](https://aws.amazon.com/free/).

_**WARNING**_: Although a new AWS account has a free tier, the nature of EKS is not completely covered by the free tier, and some costs are expected. You can use the [AWS Pricing Calculator](https://calculator.aws/#/) to estimate your costs, assuming you have studied the CloudFormation templates and know which services will be created. Based on experience (from early 2022), you can expect around charges of less than US$10 per day of running all the stacks.

> If you are planning to use this just for learning or experimentation, please consider deleting all stacks as soon as possible.

## Preparing a Python Virtual Environment

_**Note**_: If you use a service like [GitPod](https://gitpod.io/), you can skip this step as you already have a unique development environment.

Once you have cloned this repository, change into the project directory and run the following commands:

```shell
# Create the Virtual Environment
python3 -m venv venv

# Change into the virtual environment
. venv/bin/activate
```

## Preparing AWS IAM Permissions

TODO

