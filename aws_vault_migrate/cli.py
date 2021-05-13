#/usr/bin/env python

import configparser

import os
import argparse
import shlex, subprocess


def main():
    AWS_CONFIG_PATH=os.path.expanduser(os.environ.get('AWS_CONFIG_PATH', "~/.aws/config"))
    AWS_CREDENTIAL_PATH=os.path.expanduser(os.environ.get('AWS_CREDENTIALS_PATH', "~/.aws/credentials"))

    parser = argparse.ArgumentParser(description='Migrate from plain text AWS Cli credential file to aws-vault.')
    parser.add_argument('--remove', action='store_true',
                        help='Remove the secret from credentials file')

    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(AWS_CONFIG_PATH)
    credentials = configparser.ConfigParser()
    credentials.read(AWS_CREDENTIAL_PATH)

    vault_env = os.environ.copy()
    for var_key in vault_env.copy():
        if var_key.startswith("AWS_"):
            del vault_env[var_key]

    for section in config.sections():
        profile_name = section.replace("profile ","")

        if credentials.has_section(profile_name):
            #aws_access_key_id = credentials[profile_name]['aws_access_key_id']
            #aws_secret_access_key = credentials[profile_name]['aws_secret_access_key']
            vault_env["AWS_ACCESS_KEY_ID"] = credentials[profile_name]['aws_access_key_id']
            vault_env["AWS_SECRET_ACCESS_KEY"] = credentials[profile_name]['aws_secret_access_key']
            command_args = shlex.split("aws-vault add %s --env" % (profile_name,))
            aws_vault_cmd = subprocess.Popen(command_args, env=vault_env,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
            aws_vault_cmd.wait()
            stdout, stderr = aws_vault_cmd.communicate()
            if stderr:
                print(stderr)
            else:
                if args.remove:
                    credentials.remove_section(profile_name)

    with open(AWS_CREDENTIAL_PATH, 'w') as credentialfile:
        credentials.write(credentialfile)


if __name__ == "__main__":
    main()