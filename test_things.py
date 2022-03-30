import boto3
import sure
from moto import mock_ec2
from moto.autoscaling import mock_autoscaling

from things import get_autoscaling_groups

@mock_autoscaling
def test_something():


    mocked_networking = setup_networking()
    as_client = boto3.client("autoscaling", region_name="us-east-1")
    as_client.create_launch_configuration(
        LaunchConfigurationName="tester_config",
        ImageId='ami-12c6146b',
        InstanceType="t2.medium",
    )

    as_client.create_auto_scaling_group(
        AutoScalingGroupName="tester_group",
        LaunchConfigurationName="tester_config",
        MinSize=2,
        MaxSize=2,
        VPCZoneIdentifier=mocked_networking["subnet1"],
    )

    group = as_client.describe_auto_scaling_groups()["AutoScalingGroups"][0]
    group["AutoScalingGroupName"].should.equal("tester_group")
    group["MaxSize"].should.equal(2)
    group["MinSize"].should.equal(2)
    group["LaunchConfigurationName"].should.equal("tester_config")

    group["AvailabilityZones"].should.equal(["us-east-1a"])  # subnet1
    group["DesiredCapacity"].should.equal(2)
    group["VPCZoneIdentifier"].should.equal(mocked_networking["subnet1"])
    group["DefaultCooldown"].should.equal(300)
    group["HealthCheckGracePeriod"].should.equal(300)
    group["HealthCheckType"].should.equal("EC2")
    group["LoadBalancerNames"].should.equal([])
    group.shouldnt.have.key("PlacementGroup")
    group["TerminationPolicies"].should.equal([])
    group["Tags"].should.equal([])

    # get_autoscaling_groups(['bar'])

@mock_ec2
def setup_networking(region_name="us-east-1"):
    ec2 = boto3.resource("ec2", region_name=region_name)
    vpc = ec2.create_vpc(CidrBlock="10.11.0.0/16")
    subnet1 = ec2.create_subnet(
        VpcId=vpc.id, CidrBlock="10.11.1.0/24", AvailabilityZone=f"{region_name}a"
    )
    subnet2 = ec2.create_subnet(
        VpcId=vpc.id, CidrBlock="10.11.2.0/24", AvailabilityZone=f"{region_name}b"
    )
    return {"vpc": vpc.id, "subnet1": subnet1.id, "subnet2": subnet2.id}
