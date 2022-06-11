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

In addition you must obviously also have access to AWS. If you do not yet have an account, head over to [AWS and create a free account](https://aws.amazon.com/free/).

In terms of basic knowledge and experience that is required to follow along, consider the following as minimum:

* Good working knowledge of common Linux commands, including tools like `vim`, `tar`, `less`, `tail`, `cat`, `grep` etc. 
* Be comfortable with navigating the Linux filesystem
* Understand concepts like STDIN and STDOUT, pipes, redirection etc.
* Know how to install software using a package manager (`apt` or `rpm` - based on your distribution of choice)
* Have some basic prior experience in provisioning and using AWS services like `S3`, `EC2`, `Lambda` etc. Working knowledge of `CloudFormation` is also required. Be comfortable using the AWS CLI.

_**WARNING**_: Although a new AWS account has a free tier, the nature of EKS is not completely covered by the free tier, and some costs are expected. You can use the [AWS Pricing Calculator](https://calculator.aws/#/) to estimate your costs, assuming you have studied the CloudFormation templates and know which services will be created. Based on experience (from early 2022), you can expect around charges of less than US$10 per day of running all the stacks. You may also want to check out how you can [control your AWS costs as described in this AWS page](https://aws.amazon.com/getting-started/hands-on/control-your-costs-free-tier-budgets/)

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

## AWS Account Preparations

Creating a new AWS account should also create you a default VPC. This will be 100% fine to use as the "public" VPC.

Consider using an EC2 instance in the public VPC from where AWS CLI commands can be run. The AWS Administrator role could be assigned to this EC2 instance, as you will need to deploy CloudFormation templates and also run various AWS CLI commands. 

_**WARNING**_: For better security, use the EC2 instance with no execution role attached amd once logged in, manually set the AWS credentials of an IAM user with API credentials. Using environment variables are recommended, for example, you could use the following:

```shell
export AWS_ACCESS_KEY_ID=XXXXXXXXXXXXXXXXXXXX
export AWS_SECRET_ACCESS_KEY=xxxXXXxxxXXXxxxXXXxxxXXXxxxXXXxxxXXXxxxX
export AWS_REGION=eu-central-1
export AWS_DEFAULT_REGION=eu-central-1
export AWS_DEFAULT_OUTPUT=yaml
export AWS_PAGER=less
```

> Once you log out of the EC2 terminal session, or when the EC2 instance is stopped, the environment variables are deleted.

If you plan to use an EC2 instance to also deploy the CloudFormation stacks and run the other commands, note the pre-requisites listed above and ensure that it is also installed on the Instance.

TODO - Provide an example CloudFOrmation template to provision an EC2 instance that can be used as Jump Host and from where all commands could be executed.
