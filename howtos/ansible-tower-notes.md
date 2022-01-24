These notes come from evaluating Ansible Tower for managing WebRouter and Custom Domain instances.

## Need a separate venv

The `setup-web-router.yml` file needs to use the aws cli to determine if the ECR has any images in it.  
Just installing the AWS CLI yum RPM does not work because that version of the AWS cli has a version 
mismatch with the Python libraries stored in the Ansible Tower venv.

We will use this as an opportunity to test out creating a separate venv for AWS projects using the 
following procedure:

https://docs.ansible.com/ansible-tower/latest/html/upgrade-migration-guide/virtualenv.html

We did need to install gcc on the system in order for Python to build local versions.  We use the following Python requirements file for AWS environments:

```
ansible
awscli>=1.19.103,<2.0
boto3>=1.17.103,<2.0
jq>=1.1,<2.0
psutil
```

Once the environment is set up then one needs to go into the Tower System Settings and add the /opt/my-envs directory to the "Custom Virtual Environment Paths" directory.  Once that is done then Templates will have an "Ansible Environment" option with a list of the ones that Tower finds.  

If the venv does not show up then double-check the permissions on the venv -
the default umask as per InfoSec is 027 whereas the venv build process needs
022.



