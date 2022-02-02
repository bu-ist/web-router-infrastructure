## Building a Cloudfront virtual host

Once we create a CloudFront distribution we do not want to have to change it if at all posible. To make that
possible we are building CloudFront distributions using a completely separate CloudFormation template from
the other infrastructure.  This means that the CloudFront distributions will not be nested with another stack
nor import any values from another stack.

Right now we are naming the CloudFormation stacks buaws-site-dashedhostname where dashedhostname is the hostname
with all dots converted to dashes. For example `www-syst.bu.edu` becomes `www-syst-bu-edu` - this is because
CloudFormation stacks are not allowed to have dots in their name.

This does mean that one needs to do the following process to get up a new CloudFront distribution/virtual host:

1. Import the InCommon SSL certificate into acm and record the ARN of the certificate.  This common name in the
   certificate becomes the Alias in the CloudFormation template.

2. Determine the WebACL value by looking at the WAFWebACL output of the buaws-webrouter-landscape-waf stack.

3. Determine the CloudFront log bucket by looking at the AccessLogBucket parameter of the
   buaws-webrouter-landscape-waf stack.  Append `.s3.amazonaws.com` to the value to get the LogBucket parameter
   of the CloudFront stack.

4. Determine the RoutingOriginDNS entry by looking at the WebRouterDNS output from the buaws-webrouter-main-landscape
   stack.

5. Build the settings file for this virtual host in cloudfront/settings/stackname-parameters.json.

## How to calculate the memory and CPU size parameters

We are taking advantage of the target-based scaling for ECS to try and simplify this.  Also, we are scaling both ECS
and EC2 based on CPU values - actual CPU usage for ECS and reserved CPU for the EC2 instances.  Memory is not an
issue with NGINX so we don't have to worry about that.

Based on the results of load testing we might want to switch ECS to ALBRequestCountPerTarget.  That way we could scale
to keep ~500-600 connections to each NGINX container which is well under the 1024 maximum NGINX is currently set to.
This should only be done if load testing shows that this version does not work properly.

## GitHub token

We store the GitHub token as a secret in the AWS Secrets Manager.  There is one secret per account and you can check 
if the secret is present by not getting an error when you do the following command:

```bash
$ aws --profile x secretsmanager get-secret-value --secret-id websites-webrouter/dockerhub-credentials --query SecretString
aws --profile websites-prod secretsmanager get-secret-value  --secret-id  websites-webrouter-dockerhub-secret --query SecretString

An error occurred (ResourceNotFoundException) when calling the GetSecretValue operation: Secrets Manager can't find the specified secret.
```

You can create a secret by creating a JSON file similar to `sample-secret.json` and doing the following command:

```bash
$ aws --profile x secretsmanager create-secret --name GitHubTokenSecret/WebRouter --secret-string file://github-token.json
{
    "ARN": "arn:aws:secretsmanager:us-east-1:acctid:secret:GitHubTokenSecret/WebRouter-Fue6rj",
    "Name": "GitHubTokenSecret/WebRouter",
    "VersionId": "cb05b4ea-ed64-4f72-8777-0eaf1f90f0b4"
}
```

## DockerHub login

We store the DockerHub username and password as a secret in AWS Secrets Manager.  There is one secret per account and you can check
if the secret is present by doing the following command - if you get the error shown then it doesn't exist:

```bash
$ aws --profile x secretsmanager get-secret-value --secret-id websites-webrouter/dockerhub-credentials --query SecretString
aws --profile websites-prod secretsmanager get-secret-value  --secret-id  websites-webrouter-dockerhub-secret --query SecretString

An error occurred (ResourceNotFoundException) when calling the GetSecretValue operation: Secrets Manager can't find the specified secret.
```

You can create a secret by creating a JSON file similar to `sample-secret.json` and doing the following command:

```bash
$ aws --profile x secretsmanager create-secret --name websites-webrouter/dockerhub-credentials --secret-string file://dockerhub.json
{
    "ARN": "arn:aws:secretsmanager:us-east-1:acctid:secret:websites-webrouter/dockerhub-credentials-RAnCED",
    "Name": "websites-webrouter/dockerhub-credentials",
    "VersionId": "4a2ea896-8ca4-420c-9b93-fa96e13e9609"
}
```

## WebRouter account setup

These are the one-time steps necessary to prepare an account for the WebRouter.  

1. If the VPC has not been created for this landscape, this will create it.
** Run the base-landscape stack: `./create-stack.sh awsprofile region vpc buaws-{vpc-name} --capabilities CAPABILITY_IAM`

Example:

```bash
./create-stack.sh default us-west-2 vpc buaws-websites-dr-prod --capabilities CAPABILITY_IAM
```

2. Do these steps to create the WAF NOTE: not needed for dr testing.

	a. Use console Cloudformation create stack

      b. From s3 https://s3.amazonaws.com/buaws-websites-{prod or nonprod}-us-east-1/aws-waf-security-automations/aws-waf-security-automations.template

      c. Name is buaws-webrouter-{landscape}-waf
      Example `buaws-webrouter-prod-waf`

      d. CloudFront Access Log Bucket Name from buaws-webrouter-base-{landscape} LogBucketARN (without arn:aws:s3::: part)
      Example from `buaws-webrouter-base-prod`  LogBucketARN: `buaws-webrouter-base-prod-logbucket-qbfzl6a67kpv`

      e. set WAFTriggerAction to count

      f. Capabilities be sure to acknowledge `I acknowledge that AWS CloudFormation might create IAM resources.`

      g. click through the defaults and create the stack.

## Ansible system setup

`ist-aws-toolbox` is already set up to run these Ansible playbooks using a special Python virtual environment.  You
should activate the using the `/opt/ansible/bin/activate` script as such:

```bash
[dsmk@ist-aws-toolbox ~]$ . /opt/ansible/bin/activate
(ansible) [dsmk@ist-aws-toolbox ~]$
```

The following instructions are in case you want to run this on a different system such as a Mac laptop.  You will 
want to have the following:
1. AWS credentials (either access/secret key or Docker plus `awslogin` script)
2. Ansible
3. The two AWS collections installed locally as documented here:

```bash
$ ansible-galaxy collection install -r collections/requirements.yml
Process install dependency map
Starting collection install process
Skipping 'amazon.aws' as it is already installed
Skipping 'community.aws' as it is already installed
```

## Building/maintaining a blue/green environment for a specific landscape (DR site question?)

The `setup-web-router.yml` and `delete-web-router.yml` Ansible playbooks can be used to manage instances of the WebRouter.
Right now they do not incorporate any CloudFront changes but rather build the underlying WebRouter including its
CI/CD pipeline.  

The playbooks take two parameters:

- _landscape_ : The landscape that this WebRouter instance is a part of.
- _color_ : The color name of the system being managed.  This is not limited to blue/green but can be any alphanumeric text less than 7-8 characters.

All other variables are stored in Ansible variable files located in the `vars` subdirectory.  

This presumes that you have completed the steps [WebRouter account setup](#webrouter-account-setup) and [Ansible system setup](#ansible-system-setup). Make certain that you have done `awslogin` and have CD'ed to the root of this GitHub repo.

The command for creating and updating a WebRouter instance is the same:

```bash
$ ansible-playbook -e landscape=syst -e color=blue setup-web-router.yml
[snipped output]


PLAY RECAP ******************************************************************************************************************
localhost                  : ok=12   changed=8    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0   
```

One can add `--check` to the command line to see what changes the stack will make.  For now this will always show that the main-landscape stack will change because of some CloudFormation nested stack interactions.

Building a brand new WebRouter instance will take approximately 25-40 minutes.  You might want to watch/check especially
the main landscape stacks using the AWS Web Console to monitor the CloudFormation stacks.

If the build fails waiting for the CodePipeline to run then you should check the CodePipeline with the AWS Web Console 
because it may have encountered a GitHub API error.  If so, wait a few minutes and click the "Release Change" button 
to have the pipeline try again.  Once the CodePipeline has completed successfully then you can re-run the 
`setup-web-router.yml` and it will finish the installation.

## Common release workflow

1. Build the new color landscape a day or two before the change date and do internal testing.  This testing can either be
   testing the WebRouter instance directly or repointing a less significant CloudFront to this WebRouter instance.

2. During the change window repoint the CloudFront instances to the new WebRouter instance and do smoke testing.  Do not 
   delete the previous WebRouter instance as this will provide a quick rollback option during the initial release.

3. A few days later delete the old WebRouter instance using the `delete-web-router.yml` Ansible playbook.

Note: During the initial transition to the new approach step 3 will need to be different.  That is because the 
base and iam stacks of the non-blue/green infrastructure are used by the old WAF version 1 implementation (and the 
CloudFront logs which are examined by our WAFv1 implementation).  In that case 
we would manually delete the landscapes' main-landscape stack (`buaws-webrouter-main-syst` for example) to minimize 
the overhead of that infrastructure.

## VPC VPN configuration

The problems with letting AWS automatically calculate the tunnel addresses are two-fold:
1) Ideally we want repeatability of usage (so rerunning the CloudFormation uses a similar configuration).
2) Avoiding the case where the customer gateway has a conflict because the tunnel address was already used by another account.

Really the second issue is the important one for us (the first will be more important when we include the
pre-shared key in the CloudFormation).

Anyway, the following AWS documentation talks about the accepted values for the tunnel cidrs:

https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-vpnconnection-vpntunneloptionsspecification.html.

The short answer is that we should use /30 cidrs in the 169.254.0.0/16 range avoiding a bunch of /30s listed in the
above documentation.


# older stuff


Starting to look into using nested stack sets for some of this.  This means that the CF templates need to
be stored in an S3 bucket.  This approach uses the approach similar to:

https://github.com/awslabs/ecs-refarch-continuous-deployment

This means that one of the first things we need to do is run the deploy script to create, configuration, and
update the S3 bucket that contains the CF templates.  Once that is done one can run cloudformation referencing
the S3 bucket location.  This requires the following changes to the process:

1. separate the settings files into separate trees from the templates.
2. put the templates all in a single tree in bucket/templates/landscape/
3. move the parameters into separate directories.

These CloudFormation templates are used to provision and manage the BU IS&T Web2Cloud phase 1 project
infrastructure.  Each subdirectory is a different cloudformation stack to be run independently due to
lifecycle, number, or policy.  Some of them export values to be used by other stacks (for example, vpc).

Each subdirectory has a settings subdirectory to store parameters and tags for specific instances of the
stack.

It consists of the following stacks:

- account : account level settings irrespective of landscape (web2cloud-prod, and web2cloud-nonprod).
- vpc : this stack builds the VPC and conditionally VPN connections back to campus (web2cloud-prod, web2cloud-nonprod, and sandbox).
- base-landscape : this contains the common per landscape elements (basic ECR and S3 buckets)
  (buaws-webfe-base-syst, buaws-webfe-base-devl, buaws-webfe-base-test, buaws-webfe-base-qa, buaws-webfe-base-prod)
- iam-landscape : this contains iam definitions per landscape elements
  (buaws-webfe-iam-syst, buaws-webfe-iam-devl, buaws-webfe-iam-test, buaws-webfe-iam-qa, buaws-webfe-iam-prod)
-

The basic deployment workflow for non-production and www-syst will be:

1. Set up the account (right now this is a manual but well-defined process with local accounts (federation later).
2. Run the vpc stack with the web2cloud-nonprod settings.
3. Do the AWS side of the VPN connection (if not done by the vpc stack settings).
4. Run the base-landscape stack with the buaws-webfe-base-syst settings.
5. Run the iam-landscape stack with the buaws-webfe-iam-syst settings (by InfoSec).
6. Run the ecs-landscape stack with the buaws-webfe-ecs-syst settings.
7. Run the cloudfront-landscape stack with the buaws-webfe-cf-syst settings.


This top-level directory contains some simple shell scripts that are mainly wrappers around the standard
CLI.  This was done for two reasons: 1) consistency of execution by multiple parties; and 2) as a learning
aid for understanding the AWS cli options for CloudFormation.

The current scripts are:

- create-stack.sh - creates a stack from scratch (for initial build).
- update-stack.sh - updates a stack immediately (mainly for initial development).
- changeset-create.sh - creates a changeset on what would change if one updated the template and settings.
- changeset-describe.sh - shows the contents of a changeset
- validate-template.sh - validates that a CF template is in the correct format.

Right we do not have any commands to delete a stack or delete/execute change sets.  This process can be done
through the console.

Things to be aware of:
1. deleting IAM roles from iam-landscape will not delete them from the system, just from being tracked by CF
2. one needs to add the --capabilities CAPABILITY_IAM to the end of the create/update stack options.  For example,  ./update-stack.sh w2c-nonprod iam-landscape buaws-webfe-iam-syst --capabilities CAPABILITY_IAM

----
Old readme


The CloudFormation templates in this directory set up www-test.bu.edu infrastructure - the test landscape for the
core bu.edu web service.  It is split into multiple templates for two reasons: 1) because they are various quick
starts, examples, and reference architectures stiched together; and 2) I wanted to start separating by role
(3-iam.yaml has everything that InfoSec would manage).

The templates should be run in the following order:

- need to create the basic account stuff and the initial keypair.
- 1-vpc - creates the core VPC configuration
- 2-deployment-base - creates the basic ECR and S3 buckets - needs to be done before iam so the S3 buckbets can be referenced
- 3-iam - all security groups and IAM roles
- 4-ecs-buedu (rename) - application load balancer and ECS cluster
- Run 5-deploy-buedu to store ecs-buedu-service.yaml in a Zip and upload to the S3 bucket (this still needs to be made generic - has a hardcoded bucket name)
- 6-deployment-pipeline - The CodeBuild, CodePipeline, and CodeDeploy definitions which does the automatic release when the GitHub repo is updated.  The pipelines uses the zipped ecs-buedu-service to manage release.
- 7-cloudfront.yaml - sample CloudFront distribution to be used as an example.

The templates in this directory are based on the following sources:

- http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/quickref-ecs.html
- https://aws.amazon.com/blogs/compute/continuous-deployment-to-amazon-ecs-using-aws-codepipeline-aws-codebuild-amazon-ecr-and-aws-cloudformation/

Eventually we will incorporate items from the following sources:

- http://docs.aws.amazon.com/codebuild/latest/userguide/how-to-create-pipeline.html#how-to-create-pipeline-add-test
- https://aws.amazon.com/blogs/aws/codepipeline-update-build-continuous-delivery-workflows-for-cloudformation-stacks/
- http://docs.aws.amazon.com/codecommit/latest/userguide/how-to-migrate-repository-existing.html
- https://sanderknape.com/2016/06/getting-ssl-labs-rating-nginx/
- https://aws.amazon.com/blogs/compute/continuous-deployment-for-serverless-applications/
- https://github.com/awslabs/aws-waf-security-automations
- https://sanderknape.com/2017/06/infrastructure-as-code-automated-security-deployment-pipeline/
- https://github.com/andreaswittig/codepipeline-codedeploy-example


Various methods to test with CodePipeline:
- https://aws.amazon.com/blogs/devops/implementing-devsecops-using-aws-codepipeline/

How to do this with an external continuous integration other than CodePipeline (CircleCI):
- https://circleci.com/docs/1.0/continuous-deployment-with-aws-ec2-container-service/

Here are some documents used for how to handle redirection:

https://aws.amazon.com/blogs/compute/build-a-serverless-private-url-shortener/ (S3 redirect single URLs)


aws --profile webpoc cloudformation validate-template --template-body file:///home/dsmk/projects/docker-bufe-buedu/aws/iam.yaml

VPC: This can be done with the CLI doing something like:

aws --profile webpoc cloudformation create-stack --template-body file://1-vpc.yaml --tags file://non-prod-vpc-tags.json --parameters file://non-prod-vpc-parameters.json --stack-name vpctest

https://github.com/pahud/ecs-cfn-refarch/blob/master/cloudformation/service.yml
