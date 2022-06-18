"""
This script will:

    * Create an SSH  keypair and store the Private key temporarily in memory
    * Create an AWS secret to store the private key

Use the script create_local_ssh_private_key.py to get a copy of the key from AWS SecretsManager and create a local private key
"""

import boto3
import traceback
import os
import copy
import argparse

# Reference: https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html#configuration-envvars-runtime
AWS_REGION = os.getenv('AWS_REGION', 'eu-central-1')

###############################################################################
###                                                                         ###
###        P A R S E    C O M M A N D    L I N E   A R G U M E N T S        ###
###                                                                         ###
###############################################################################


def parse_command_line_arguments(): # pragma: no cover
    try:
        parser = argparse.ArgumentParser(description='Create an EC2 key pair and store the private certificate in AWS SecretsManager')
        parser.add_argument(
            '--key-pair-name',
            dest='key_pair_name',
            metavar='STRING',
            type=str,
            nargs=1,
            required=True,
            help='The name of the SSH Key Pair'
        )
        return parser.parse_args()
    except:
        traceback.print_exc()
    return None


###############################################################################
###                                                                         ###
###           A W S    I N T E G R A T I O N    F U N C T I O N S           ###
###                                                                         ###
###############################################################################


def get_aws_api_client(
    service_name: str="ec2", 
    client_class=boto3.client,
    aws_region: str='eu-central-1'
):
    return client_class(service_name, region_name=aws_region)


def get_key_pair_names(client)->list:
    names = list()
    try:
        response = client.describe_key_pairs()
        if 'KeyPairs' in response:
            for key_pair_config in response['KeyPairs']:
                if 'KeyName' in key_pair_config:
                    names.append(key_pair_config['KeyName'])
    except:
        traceback.print_exc()
    return names


def create_key_pair(client, name: str)->dict:
    key_data = dict()
    key_data['KeyMaterial'] = None
    try:
        response = client.create_key_pair(KeyName=name)
        if 'KeyMaterial' in response:
            key_data = copy.deepcopy(response)
    except:
        traceback.print_exc()
    return key_data


def create_key_pair_secret(client, key_data:dict)->bool:
    try:
        name = 'ec2_key_pair_{}'.format(
            key_data['KeyName']
        )
        response = client.create_secret(
            Name=name,
            Description='RSA Private Key to enable SSH access to EC2 instances',
            SecretString=key_data['KeyMaterial'],
            ForceOverwriteReplicaSecret=True
        )
        if 'ARN' in response:
            print('Secret created. ARN={}'.format(response['ARN']))
            return True
    except:
        traceback.print_exc()
    return False


def delete_key_pair(client, name: str):
    try:
        client.delete_key_pair(KeyName=name)
    except:
        traceback.print_exc()


###############################################################################
###                                                                         ###
###                                 M A I N                                 ###
###                                                                         ###
###############################################################################

def main(
    args=parse_command_line_arguments(),
    client_class=boto3.client
):
    ec2_client = get_aws_api_client(service_name='ec2', client_class=client_class, aws_region=AWS_REGION)
    secretsmanager_client = get_aws_api_client(service_name='secretsmanager', client_class=client_class, aws_region=AWS_REGION)
    existing_key_pair_names = get_key_pair_names(client=ec2_client)

    key_pair_name = args.key_pair_name[0]

    if key_pair_name in existing_key_pair_names:
        raise Exception('Keypair with name "{}" already exists'.format(key_pair_name))
    key_data = create_key_pair(client=ec2_client, name=key_pair_name)
    if key_data['KeyMaterial'] is None:
        raise Exception('FAILED to create key pair named "{}"'.format(key_pair_name))
    if create_key_pair_secret(client=secretsmanager_client, key_data=key_data) is False:
        print('FAILED to create secret - attempting to roll back key_pair creation. If this step fails for some reason, you need to manually delete the key in the EC2 console.')
        delete_key_pair(client=ec2_client, name=key_pair_name)
    print('DONE')
    

if __name__ == "__main__":
    main()

# EOF
