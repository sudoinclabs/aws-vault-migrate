from setuptools import setup, find_packages

#with open('requirements.txt') as f:
#    requirements = f.readlines()

long_description = 'AWS-Vault migrate to help migrate from plain text credentials \
      to more secure aws-vault stored secrets'

setup(
        name ='aws-vault-migrate',
        version ='0.1.0',
        author ='Hameedullah Khan',
        author_email ='hameed@sudo.inc',
        url ='https://github.com/sudoinclabs/aws-vault-migrate',
        description ='AWS Vault Migrate will allow seemless migration from plain text credentials',
        long_description = long_description,
        long_description_content_type ="text/markdown",
        license ='MIT',
        packages = find_packages(),
        entry_points ={
            'console_scripts': [
                'aws-vault-migrate=aws_vault_migrate.cli:main'
            ]
        },
        classifiers = [
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        keywords ='aws-vault aws-vault-migrate  python package sudoinclabs',
        zip_safe = False
)