#!/usr/bin/env python


import boto3
import logging

import os
import sys
import json

from jinja2 import Environment, FileSystemLoader

# LOG_LEVEL=os.environ['LOG_LEVEL']
if not os.environ.get('LOG_LEVEL'):
    logLevel = 'INFO'
else:
    logLevel = os.environ['LOG_LEVEL']

logger = logging.getLogger()
logger.setLevel(logLevel)
logging.captureWarnings(True)

# create file handler which logs even debug messages
fh = logging.StreamHandler(sys.stdout)
fh.setLevel(logging.WARN)

# create console handler with a higher log level
ch = logging.StreamHandler(sys.stderr)
ch.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


def get_account_ids(sns_msg_jsn):
    try:

        accountIds = []

        for account in sns_msg_jsn['accountids']:
            print('Account ID {0}'.format(account))
            accountId = account
            accountIds.append(accountId)

        print("Accounts {0}".format(json.dumps(accountIds)))
        return accountIds

    except Exception as e:
        logger.error("ERROR: ")
        logger.error("-- get_account_ids -- ERROR: {0}".format(str(e)))
        raise
    finally:
        logger.info("-- get_account_ids -- Finished")


def policy_document_from_jinja(accountIds, current_account_id, policy_name, secretArn,**kwargs):
    # Try and read the policy file file into a jinja template object
    policy_path = "./templates"
    policy_file = policy_name + ".j2"

    if 'bucketName' in kwargs:
       bucket_name = kwargs.get('bucketName', None)
    else:
        bucket_name = current_account_id + '-' + policy_name


    try:
        root = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(root, 'templates')
        env = Environment(loader=FileSystemLoader(templates_dir))
        template = env.get_template(policy_file)
        print("ENV = {0}".format(env))
        print("Template Dir ==> {0}".format(templates_dir))
    except Exception as e:
        raise ValueError(
            "Failed to read template file {}/{}\n\n{}".format(
                policy_path,
                policy_file,
                e
            )
        )

    try:

        if secretArn == "false":
            template_jinja = template.render(
                account_ids=accountIds,
                ss_account_id=current_account_id,
                bucket_name=bucket_name
            )
        else:
            template_jinja = template.render(
                account_ids=accountIds,
                ss_account_id=current_account_id,
                secretArn=secretArn
            )

        print("Rendered Template {}".format(template_jinja))
    except Exception as e:
        raise ValueError(
            "Jinja render failure working on file {}/{}\n\n{}".format(
                policy_path,
                policy_file,
                e
            )
        )
    return (template_jinja)


def set_s3_bucket_policy(bucket_name, s3PolicyDoc, ss_account_id):
    try:

        s3 = boto3.resource('s3')
        bucket_policy = s3.BucketPolicy(bucket_name)

        response = bucket_policy.put(
            ConfirmRemoveSelfBucketAccess=False,
            Policy=s3PolicyDoc
        )

    except Exception as e:
        logger.error("ERROR: ")
        logger.error("-- set_s3_bucket_policy -- ERROR: {0}".format(str(e)))
        raise
    finally:
        logger.info("-- set_s3_bucket_policy -- Finished")


def lambda_handler(event, context):
    try:
        sts = boto3.client('sts')
        response = sts.get_caller_identity()
        current_account_id = response['Account']
        message = event['Records'][0]['Sns']['Message']
        jsonMessage = json.loads(message)
        accountIds = get_account_ids(jsonMessage)

        for policyInfo in jsonMessage['policyNames']:
            policyType = policyInfo['type']
            policyName = policyInfo['name']
            if  policyType == 's3':
                region = policyInfo['region']
                print('Bucket Policy Region {0}'.format(region))
                bucket_name = current_account_id + "-" + region + "-" + policyName
                print('Bucket Name {0}'.format(bucket_name))
                s3PolicyDoc = policy_document_from_jinja(accountIds, current_account_id, policyName, "false", bucketName=bucket_name)
                set_s3_bucket_policy(bucket_name, s3PolicyDoc, current_account_id)
    except Exception as e:
        logger.error("ERROR: ")
        logger.error("-- lambda_handler -- ERROR: {0}".format(str(e)))
        raise
    finally:
        logger.info("-- lambda_handler -- Finished")


def main():
    bucket_name = "111111111111-ss-cf-templates"
    ss_account_id = "111111111111"
    accountIds = get_account_ids()
    s3PolicyDoc = policy_document_from_jinja(accountIds)
    set_s3_bucket_policy(bucket_name, s3PolicyDoc, ss_account_id)


if __name__ == '__main__':
    main()
