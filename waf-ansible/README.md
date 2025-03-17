

## waf-ansible
- Build an AWS WAF.
- Adjust the WAF using a combo of Ansible and Python.


Sample Json parameter file.

```json
[
    {
        "ParameterKey": "LogPrefix",
        "ParameterValue": "websites-webrouter-alb-logs-sandbox"
    },
    {
        "ParameterKey": "DeliveryStreamName",
        "ParameterValue": "websites-webrouter-waf-logs-sandbox"
    },
    {
        "ParameterKey": "EndpointType",
        "ParameterValue": "CloudFront"
    },

```

To build a WAF stack:

```bash
./update.py --region us-east-1 waf-ansible/settings/websites-webrouter-sandbox-waf-v2-parameters.json --wait --iam
```

To update WAF stack:  NOTE: this does not change rules!
```bash
./update.py --region us-east-1 waf-ansible/settings/websites-webrouter-sandbox-waf-v2-parameters.json --wait --iam
```

## To update rules
Rules are organized by landscape, make your adjustmnts to the rules.
```yaml
    landscapes:
      sandbox:
        WebACLName: websites-webrouter-sandbox-waf-v2-WAF-DGSR10BM5BEK
        WebACLID: 96f3c0af-9e3d-4212-a87d-1cbb56f244be
        Region: us-east-1
        Scope: CLOUDFRONT
        arn: arn:aws:wafv2:us-east-1:847284185857:global/webacl/websites-webrouter-sandbox-waf-v2-WAF-DGSR10BM5BEK/96f3c0af-9e3d-4212-a87d-1cbb56f244be
        WhitelistRule: Allow
        BlacklistRule: Allow
        ReputationListsRule: Block
        BadBotRule: Allow
        # "AWS-AWSManagedRulesCommonRuleSet",
        SqlInjectionRule: Allow
        XssRule: Allow
        ScannersAndProbesRule: Allow
        HttpFloodRateBasedRule: Count
```

To make changes to the sandbox landscape:
1. make sure you are lgged into the correct aws account
```bash
[hl-c@ist-aws-toolbox waf-ansible]$ awswhoami
Running 'aws sts get-caller-identity'
Account: 847284185857
ARN:  arn:aws:sts::847284185857:assumed-role/Shibboleth-InfraMgt/hl-c@bu.edu
Account Alias:  iam-sandbox
```

2. Activate Python Virtual environment
```bash
~/ansible/bin/activate
```

3. Run the update
```bash
ansible-playbook update-websites-webrouter-waf-v2.yaml -e "target_env=sandbox"
```

4. Review the output of the changes:
```bash
(ansible) [hl-c@ist-aws-toolbox waf-ansible]$ ansible-playbook update-websites-webrouter-waf-v2.yaml -e "target_env=sandbox"
[WARNING]: provided hosts list is empty, only localhost is available. Note that the implicit localhost does not match 'all'

PLAY [update-websites-webrouter-waf-v2] ************************************************************************************************************************

TASK [Print Selected Landscape Details] ************************************************************************************************************************
ok: [localhost] => {
    "msg": "Environment: sandbox, Name: websites-webrouter-sandbox-waf-v2-WAF-DGSR10BM5BEK, ID: 96f3c0af-9e3d-4212-a87d-1cbb56f244be, ARN: arn:aws:wafv2:us-east-1:847284185857:global/webacl/websites-webrouter-sandbox-waf-v2-WAF-DGSR10BM5BEK/96f3c0af-9e3d-4212-a87d-1cbb56f244be"
}

TASK [Adjust webacl json] ***************************************************************************
changed: [localhost]

TASK [Display updated WebACL JSON] *****************************************************************************************************
ok: [localhost] => {
    "waf_update_result.stdout | from_json": {
        "NextLockToken": "a3fde528-adef-47f9-a05d-df92eb3d21ef",
        "ResponseMetadata": {
            "HTTPHeaders": {
                "content-length": "56",
                "content-type": "application/x-amz-json-1.1",
                "date": "Mon, 17 Mar 2025 03:24:16 GMT",
                "x-amzn-requestid": "4b0dad2e-ecbe-49eb-9ca0-607d6fa7d6b3"
            },
            "HTTPStatusCode": 200,
            "RequestId": "4b0dad2e-ecbe-49eb-9ca0-607d6fa7d6b3",
            "RetryAttempts": 0
        }
    }
}

PLAY RECAP *******************************************************************************************************
localhost                  : ok=3    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0 
```