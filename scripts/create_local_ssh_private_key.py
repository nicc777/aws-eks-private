"""
This script will:

    * Create an SSH  keypair and store the Private key temporarily in memory
    * Create an AWS secret to store the private key

Use the script create_local_ssh_private_key.py to get a copy of the key from AWS SecretsManager and create a local private key
"""

import boto3
import traceback
import os
import argparse
import platform

# Reference: https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html#configuration-envvars-runtime
AWS_REGION = os.getenv('AWS_REGION', 'eu-central-1')

###############################################################################
###                                                                         ###
###        P A R S E    C O M M A N D    L I N E   A R G U M E N T S        ###
###                                                                         ###
###############################################################################


def parse_command_line_arguments(): # pragma: no cover
    try:
        parser = argparse.ArgumentParser(description='Retrieve EC2 Key Pair Secret Key Data from AWS SecretsManager')
        parser.add_argument(
            '--key-pair-name',
            dest='key_pair_name',
            metavar='STRING',
            type=str,
            nargs=1,
            required=True,
            help='The name of the SSH Key Pair as stored in AWS EC2'
        )
        parser.add_argument(
            '--aws_account_id',
            dest='aws_account_id',
            metavar='STRING',
            type=str,
            nargs=1,
            required=True,
            help='The AWS Account ID where the secret is stored. This will be used to derive the full secret ARN.'
        )
        parser.add_argument(
            '--secret_id',
            dest='secret_id',
            metavar='STRING',
            type=str,
            nargs=1,
            required=True,
            help='The SecretsManager secret key ID (name). This will be used to derive the full secret ARN.'
        )
        parser.add_argument(
            '--output-file',
            dest='output_file',
            metavar='STRING',
            type=str,
            nargs=1,
            required=False,
            help='An optional output file. The default will be to create the key in ~/.ssh/ with the filename the same as the key pair name'
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


def get_secret_key_from_secrets_manager(client, aws_account_id: str, secret_id: str)->str:
    """
    The ARN will be build up from the aws_account_id and secret_id, for example, to cet the ARN "arn:aws:secretsmanager:eu-central-1:AAAAAAAAAAAA:secret:ec2_key_pair_XX_X_-XXXX", the following values need to be supplied:

        aws_account_id  : AAAAAAAAAAAA
        secret_id       : ec2_key_pair_XX_X_-XXXX

    The region will be derived.
    """
    private_key_data = None
    try:
        arn = 'arn:aws:secretsmanager:{}:{}:secret:{}'.format(
            AWS_REGION,
            aws_account_id,
            secret_id
        )
        response = client.get_secret_value(SecretId=arn)
        if 'SecretString' in response:
            private_key_data = response['SecretString']
    except:
        traceback.print_exc()
    return private_key_data


def generate_output_file(key_name: str)->str:
    return '{}{}.ssh{}{}'.format(
        os.path.expanduser('~'),
        os.sep,
        os.sep,
        key_name
    )


def create_local_private_key(key_name: str, private_key_data: str, target_out_file: str=None)->bool:
    try:
        if private_key_data is None:
            print('No data to create Private Key')
        if '-----BEGIN RSA PRIVATE KEY-----' not in private_key_data:
            print('Invalid data found in private key. Cannot create local private key')
        key_file = target_out_file
        if target_out_file is None:
            key_file = generate_output_file(key_name=key_name)
        if os.path.isfile(key_file):
            print('Removing old/existing file "{}"'.format(key_file))
            os.remove(key_file)
        print('Writing data to file "{}"'.format(key_file))
        with open(key_file, 'w') as f:
            f.write(private_key_data)
        if platform.system().lower() != 'windows':
            os.chmod(key_file, 0o600)
        return True
    except:
        traceback.print_exc()
    return False


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
    aws_account_id = args.aws_account_id[0]
    secret_id = args.secret_id[0]
    output_file = args.output_file[0]

    if key_pair_name not in existing_key_pair_names:
        raise Exception('Key named "{}" not found in EC2'.format(key_pair_name))
    private_key_data = get_secret_key_from_secrets_manager(client=secretsmanager_client, aws_account_id=aws_account_id, secret_id=secret_id)
    
    result = False
    if output_file is not None:
        result = create_local_private_key(key_name=key_pair_name, private_key_data=private_key_data, target_out_file=output_file)    
    else:
        result = create_local_private_key(key_name=key_pair_name, private_key_data=private_key_data)
    if result is False:
        raise Exception('Failed to create local file')
    print('DONE')
    

if __name__ == "__main__":
    main()

# EOF