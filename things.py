import boto3

session = boto3.Session()
ag_client = session.client('autoscaling', region_name='eu-west-2')
def get_autoscaling_groups(asg_names):
    return ag_client.describe_auto_scaling_groups(AutoScailingGroupNames=asg_names)
