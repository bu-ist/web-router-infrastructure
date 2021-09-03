# POC Custom Domain configuration

## Overview

This directory has the POC approach for Custom Domains with an eye towards the 
final configuration. 

The main configuration file for this is `custom-domains.yml` 

For more information on DNS validation see:

https://docs.aws.amazon.com/acm/latest/userguide/dns-validation.html

## Provisioning process

Here is a quick summary of the expected provisioning process

1. Request from client
2. Create ACM certificate with DNS validation to deploy.  This will generate the DNS entries to validate the certificate.
3. (client, NSEG) set up DNS validation entries.  They have 72 hours to complete this process.
4. Confirm that the ACM certificate validated (AWS web console, script?)
5. Create CloudFront and set up domain configuration.  Send CloudFront name to (client, NSEG).
6. (client, NSEG) to make DNS change switching service.

## Create ACM certificate with DNS validation to deploy

Make certain that you have AWS credentials for the web2cloud-nonprod account.  By default it will use the default awscli
profile but you can set the profile by adding `-e aws_profile=profilename` to the following command lines.

To see what would change:

```bash
$ ansible-playbook -e aws_profile=profilename configure-dns.yml --check
```

To make the change:

```bash
$ ansible-playbook -e aws_profile=profilename configure-dns.yml
```

## Create CloudFront and set up domain configuration.

This script will check all the custom domains and make certain that the CloudFormation CloudFront is up to date for all domains with ISSUED ACM certificates.  
This includes setting up the CloudFront for the first time.

The nice thing about this is that the ansible CloudFormation module works properly with --check mode - making a changeset to see if there are any pending changes.

I do have an example of making check mode produce more information on what changes are still necessary.

```bash
$ ansible-playbook -e aws_profile=profilename configure-cloudfront.yml --check
```

```bash
$ ansible-playbook -e aws_profile=profilename configure-cloudfront.yml
```

## Using a local Python environment

Documentation on how to set up a local Python/Ansible environment can be found in the
`ansible-systems` repo at:

https://github.com/bu-ist/ansible-systems/blob/main/howtos/cli_setup.md