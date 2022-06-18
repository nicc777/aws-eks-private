import boto3
import argparse
import logging
import sys
import os

DEBUG = False
logger = logging.getLogger(__name__)


###############################################################################
###                                                                         ###
###      P A R S E    C O M M A N D    L I N E   A R G U M E N T S          ###
###                                                                         ###
###############################################################################


def parse_command_line_arguments(): # pragma: no cover
    try:
        parser = argparse.ArgumentParser(description='Command Line Utility to create Secrets')
        parser.add_argument(
            '--debug', 
            dest='debug', 
            default=False, 
            action='store_true',
            help='Enable debug logging'
        )
        parser.add_argument(
            '--no-debug', 
            dest='debug', 
            action='store_false',
            help='No debug logging (default)'
        )
        parser.add_argument(
            '-r', '--region',
            dest='aws_region',
            metavar='STRING',
            type=str,
            nargs=1,
            required=False,
            default=['eu-central-1'],
            help='The AWS Region'
        )
        parser.add_argument(
            '-n', '--secret-name',
            dest='secret_name',
            metavar='STRING',
            type=str,
            nargs=1,
            required=True,
            help='A descriptive name for the secret'
        )
        parser.add_argument(
            '-s', '--source-file',
            dest='source_file',
            metavar='STRING',
            type=str,
            nargs=1,
            default='',
            required=False,
            help='The content of this file will be stored in teh AWS Secret. If not supplied, STDIN is read.'
        )
        parser.add_argument(
            '-d', '--description',
            dest='description',
            metavar='STRING',
            type=str,
            nargs=1,
            required=True,
            help='A description of the type of secret stored.'
        )
        return parser.parse_args()
    except:
        pass
    return None

###############################################################################
###                                                                         ###
###      H E L P E R    F U N C T I O N S    F O R    S E T T I N G         ###
###                                                                         ###
###                U P     O U R    E N V I R O N M E N T                   ###
###                                                                         ###
###############################################################################


def logger_config():
    if DEBUG is True:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    if DEBUG is True:
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def _extract_str_from_args(
    args_data,
    empty_string_is_none: bool=False,
    convert_case: bool=False,
    convert_to_lower_case_on_convert_case_flag: bool=True
):
    final_string = ''
    if isinstance(args_data, list):
        final_string = args_data[0]
    elif isinstance(args_data, str):
        final_string = args_data
    else:
        raise Exception('Invalid Argument type')
    if final_string == '' and empty_string_is_none is True:
        return None
    if convert_case is True:
        if convert_to_lower_case_on_convert_case_flag is True:
            final_string = '{}'.format(final_string.lower())
        else:
            final_string = '{}'.format(final_string.upper())
    return final_string


def set_debug(args):
    global DEBUG
    DEBUG = args.debug


def get_data(args)->str:
    data = ''
    if _extract_str_from_args(args_data=args.source_file) == '':
        for line in sys.stdin:
            if data == '':
                data = '{}'.format(line)
            else:
                data = '{}\n{}'.format(data, line)
    else:
        with open(_extract_str_from_args(args_data=args.source_file)) as f:
            data = f.read()
    logger.info('Read {} bytes.'.format(len(data)))
    if len(data) == 0:
        logger.error('Cannot store secret with ZERO length data.')
        sys.exit(1)
    return data


###############################################################################
###                                                                         ###
###                   A W S    A P I    F U N C T I O N S                   ###
###                                                                         ###
###############################################################################


def get_aws_api_client(
    service_name: str="ec2", 
    client_class=boto3.client,
    aws_region: str=os.getenv('AWS_REGION', 'eu-central-1')
):
    return client_class(service_name, region_name=aws_region)


def create_secret(client, name: str, data: str, description: str)->str:
    if data is None:
        raise Exception('Data cannot be NoneType')
    if len(data) == 0:
        raise Exception('Data cannot be ZERO length')
    response = client.create_secret(
        Name=name,
        Description=description,
        SecretString=data,
        ForceOverwriteReplicaSecret=True
    )
    return response['ARN']


###############################################################################
###                                                                         ###
###       M A I N    A P P L I C A T I O N     E N T R Y    P O I N T       ###
###                                                                         ###
###############################################################################


def main(
    args=parse_command_line_arguments(),
    boto3_client_class=boto3.client
)->bool:
    if args is None:
        logger.error('Failed to parse command line arguments')
        exit(1)

    set_debug(args=args)
    logger_config()
    logger.info('DEBUG={}'.format(DEBUG))

    arn = create_secret(
        client=get_aws_api_client(
            service_name="secretsmanager", 
            client_class=boto3_client_class,
            aws_region=_extract_str_from_args(args_data=args.aws_region)
        ),
        name=_extract_str_from_args(args_data=args.secret_name),
        data=get_data(args=args),
        description=_extract_str_from_args(args_data=args.description)
    )
    logger.info('ARN: {}'.format(arn))

    logger.info('DONE')
    return True


if __name__ == '__main__':
    main()

# EOF
