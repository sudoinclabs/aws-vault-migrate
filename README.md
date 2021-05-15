# AWS Vault Migrate
A quick hack utility to allow you to migrate from aws cli plain text credentials to aws-vault stored secrets.


## Installation
```$ pip install aws-vault-migrate```

## Usage
```$ aws-vault-migrate```

By default it will copy the credentials to aws-vault configured storage, but will not remove them from ~/.aws/credentials file.

```$ aws-vault-migrate --remove```

To copy the secrets to aws-vault and remove them from ~/.aws/credentials file

```$ aws-vault-migrate --backend pass```

You can specify the custom backend as well to migrate to specific backend.


### Migrate from one backend to another

```$ aws-vault-migrate --source-backend file --target-backend pass```

Specify ```--source-backend``` to trigger migration from one backend to another.

