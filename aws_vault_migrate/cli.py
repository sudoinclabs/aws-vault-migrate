#/usr/bin/env python

import configparser

import os
import argparse
import shlex, subprocess
from types import new_class, prepare_class

AWS_CONFIG_PATH=os.path.expanduser(os.environ.get('AWS_CONFIG_PATH', "~/.aws/config"))
AWS_CREDENTIAL_PATH=os.path.expanduser(os.environ.get('AWS_CREDENTIALS_PATH', "~/.aws/credentials"))

class AWSVaultMigrate(object):
    """AWS Vault Migrate Class"""

    def __init__(self, args):
        super(AWSVaultMigrate, self).__init__()
        self.config = configparser.ConfigParser()
        self.config.read(AWS_CONFIG_PATH)
        self.credentials = configparser.ConfigParser()
        self.credentials.read(AWS_CREDENTIAL_PATH)

        self.args = args

    def execute(self):
        if self.args.source_backend:
            if not self.args.target_backend:
                print("Specify target backend with source")
                import sys
                sys.exit(2)
            else:
                self.backend_migrate(self.args.source_backend, self.args.target_backend)
        else:
            self.migrate_to_aws_vault()

    def prepare_env(self):
        vault_env = os.environ.copy()
        for var_key in vault_env.copy():
            if var_key.startswith("AWS_"):
                del vault_env[var_key]
        return vault_env


    def migrate_to_aws_vault(self):
        vault_env = self.prepare_env()

        for section in self.config.sections():
            profile_name = section.replace("profile ","")

            if self.credentials.has_section(profile_name):
                #aws_access_key_id = credentials[profile_name]['aws_access_key_id']
                #aws_secret_access_key = credentials[profile_name]['aws_secret_access_key']
                vault_env["AWS_ACCESS_KEY_ID"] = self.credentials[profile_name]['aws_access_key_id']
                vault_env["AWS_SECRET_ACCESS_KEY"] = self.credentials[profile_name]['aws_secret_access_key']
                command_args = shlex.split("aws-vault add %s --env" % (profile_name,))
                aws_vault_cmd = subprocess.Popen(command_args, env=vault_env,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
                aws_vault_cmd.wait()
                stdout, stderr = aws_vault_cmd.communicate()
                print(vault_env)
                if stderr:
                    print(stderr)
                else:
                    if self.args.remove:
                        self.credentials.remove_section(profile_name)

        with open(AWS_CREDENTIAL_PATH, 'w') as credentialfile:
            self.redentials.write(credentialfile)

        pass

    def backend_migrate(self, source, target):
        vault_env = self.prepare_env()
        source_vault_env = vault_env.copy()
        for section in self.config.sections():
            profile_name = section.replace("profile ","")
            if self.config.has_option(section,'sso_start_url') or self.config.has_option(section,'source_profile'):
                # Skip if 'sso_start_url' or 'source_profile' is found
                # For SSO there are no credentials to migratte
                # For source profile the credentials are migrated in another profile.
                continue
            command_args = shlex.split("aws-vault --backend %s  exec --no-session %s -- env " % (source, profile_name,))
            aws_vault_cmd = subprocess.Popen(command_args, env=source_vault_env,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
            aws_vault_cmd.wait()
            stdout, stderr = aws_vault_cmd.communicate()
            if stderr:
                print("Error:", stderr)
            else:

                found_aws_keys = False
                for aws_var in stdout.splitlines():
                    aws_var_key, aws_var_val = aws_var.split(b"=")
                    if aws_var_key in (b"AWS_ACCESS_KEY_ID",b"AWS_SECRET_ACCESS_KEY"):
                        found_aws_keys = True
                        vault_env[aws_var_key.decode("utf-8") ] = aws_var_val.decode("utf-8")
                if found_aws_keys:
                    command_args = shlex.split("aws-vault --backend %s add %s --env" % (target, profile_name,))
                    aws_vault_cmd = subprocess.Popen(command_args, env=vault_env,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
                    aws_vault_cmd.wait()
                    stdout, stderr = aws_vault_cmd.communicate()

                    if stderr:
                        print(stderr)
                    else:
                        print("Migrated successfullyy: %s" % (profile_name,))



def main():

    parser = argparse.ArgumentParser(description='Migrate from plain text AWS Cli credential file to aws-vault.')
    parser.add_argument('--backend', help='(Optional) specify the backend to use when migrating from ~/.aws/credentials file')

    parser.add_argument('--remove', action='store_true',
                        help='Remove the secret from credentials file. Ignored with backend migration.')

    parser.add_argument('--source-backend', help='Specify backend to migrate from.')
    parser.add_argument('--target-backend', help='Specify target backend to migrate to. Without source backend this is ignored.')

    args = parser.parse_args()

    aws_vault_migrate = AWSVaultMigrate(args)
    aws_vault_migrate.execute()





if __name__ == "__main__":
    main()