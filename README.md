# AWSFunctions
Retrieve information from AWS securely to support serverless apps.

This python package was created to support Slack Applications that use AWS resources. The apps and this package were 
made specifically for GRO Biosciences but may have applications beyond GRO.

## Prerequisites
Python 3.10

Python Packages: boto3, botocore, pymysql, pypika, slack_sdk

In order to use 

### AWS Resources
Systems Manager Parameter Store

Secrets Manager

Managed Relational Database (RDS)

### Slack Payload Parsing
The event payloads that are sent from Slack to an endpoint URL can be quite dense, so the AWSHelper package helps to alleviate the hassle with navigating these payloads.

Two different classes were created, BussedSlackEvent and StateMachineSlackEvent, because the event payload is 
different after being bussed via an AWS EventBridge versus after the event is passed between steps within an AWS State Machine.

### Example Application
See the repository FoundryRequests, for real world examples within a codebase for a Slack Application.

### Example
```bash
pip install AWSFunctions
```

```python
from AWSHelper import get_aws_parameter

param_val = get_aws_parameter(param_name='parameterName') 
```

As long as the environment from where you are running has the proper AWS IAM policy attached, param_val should now store the value that is encrypted within AWS Parameter Store.
