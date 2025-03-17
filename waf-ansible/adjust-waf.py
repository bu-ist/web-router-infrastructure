#!/usr/bin/python
import json
import boto3
import sys
import argparse

# Argument parser for command-line options
parser = argparse.ArgumentParser(description="Adjust WAF rule actions based on name patterns.")
parser.add_argument("--WebACLName", help="Name of WebACL")
parser.add_argument("--WebACLID", help="ID of the WebACL")
parser.add_argument("--Scope", choices=["REGIONAL","CLOUDFRONT"], help="Scope of the WebACL")
parser.add_argument("--WhitelistRule", choices=["Allow", "Block", "Count"], help="Action for Whitelist rules")
parser.add_argument("--BlacklistRule", choices=["Allow", "Block", "Count"], help="Action for Blacklist rules")
parser.add_argument("--ReputationListsRule", choices=["Allow", "Block", "Count"], help="Action for ReputationLists rules")
parser.add_argument("--BadBotRule", choices=["Allow", "Block", "Count"], help="Action for BadBot rules")
parser.add_argument("--SqlInjectionRule", choices=["Allow", "Block", "Count"], help="Action for SqlInjection rules")
parser.add_argument("--XssRule", choices=["Allow", "Block", "Count"], help="Action for Xss rules")
parser.add_argument("--ScannersAndProbesRule", choices=["Allow", "Block", "Count"], help="Action for ScannersAndProbes rules")
parser.add_argument("--HttpFloodRateBasedRule", choices=["Allow", "Block", "Count"], help="Action for HttpFloodRateBased rules")
args = parser.parse_args()

# Initialize boto3 client
client = boto3.client('wafv2', region_name='us-east-1')

# Collect webACL as a json
data = client.get_web_acl(
        Name=args.WebACLName,
        Scope=args.Scope,
        Id=args.WebACLID
    )

# Function to adjust action based on name pattern
def adjust_rule_action(rules, match, action):
    for rule in rules:
        if match in rule["Name"]:
            rule["Action"] = {action: {}}

# Example usage
adjust_rule_action(data["WebACL"]["Rules"], "WhitelistRule", args.WhitelistRule)
adjust_rule_action(data["WebACL"]["Rules"], "BlacklistRule", args.BlacklistRule)
adjust_rule_action(data["WebACL"]["Rules"], "ReputationListsRule", args.ReputationListsRule)
adjust_rule_action(data["WebACL"]["Rules"], "BadBotRule", args.BadBotRule)
adjust_rule_action(data["WebACL"]["Rules"], "SqlInjectionRule", args.SqlInjectionRule)
adjust_rule_action(data["WebACL"]["Rules"], "XssRule", args.XssRule)
adjust_rule_action(data["WebACL"]["Rules"], "ScannersAndProbesRule", args.ScannersAndProbesRule)
adjust_rule_action(data["WebACL"]["Rules"], "HttpFloodRateBasedRule", args.HttpFloodRateBasedRule)

# Output result as JSON
print(json.dumps(data, indent=4))

# WebACL update payload
response = client.update_web_acl(
    Name=args.WebACLName,
    Scope=args.Scope,
    Id=args.WebACLID,
    LockToken=data["LockToken"],
    DefaultAction={'Allow': {}},
    VisibilityConfig={
        'SampledRequestsEnabled': False,
        'CloudWatchMetricsEnabled': True,
        'MetricName': args.WebACLName
    },
    Rules=data["WebACL"]["Rules"]
)

# output response, should list nexttoken
print(json.dumps(response, indent=4))


