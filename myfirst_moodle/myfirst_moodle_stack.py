from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    Tags,
    aws_elasticloadbalancingv2 as elbv2,
    aws_elasticloadbalancingv2_targets as targets,
    aws_rds as rds, 
    aws_secretsmanager as secretsmanager,
    RemovalPolicy
)

from constructs import Construct


class MyfirstMoodleStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        #SECURTITY 
        # Create a Virtual Private Cloud (VPC) with public and private subnets
        vpc = ec2.Vpc(self, "MoodleVPC",
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),  # Explicit CIDR range
            availability_zones=["us-east-1a", "us-east-1b"],  # Explicit AZs
            nat_gateways=1,  # Allow private subnets access to the internet
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public", 
                    subnet_type=ec2.SubnetType.PUBLIC, 
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="private", 
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS, 
                    cidr_mask=24
                )
            ]
        )

        # Define separate security groups for each component
        
        # ALB Security Group - allows incoming HTTP traffic from the internet
        alb_security_group = ec2.SecurityGroup(self, "MoodleALBSecurityGroup",
            vpc=vpc,
            description="Allow HTTP traffic to ALB",
            allow_all_outbound=True
        )
        # Allow inbound HTTP traffic from anywhere to ALB
        alb_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), 
            ec2.Port.tcp(80), 
            "Allow HTTP traffic from internet"
        )
        
        # EC2 Security Group - allows incoming traffic from ALB and outbound to internet
        ec2_security_group = ec2.SecurityGroup(self, "MoodleEC2SecurityGroup",
            vpc=vpc,
            description="Allow traffic to EC2 instances from ALB",
            allow_all_outbound=True
        )
        
        # RDS Security Group - allows incoming traffic from EC2 instances only
        rds_security_group = ec2.SecurityGroup(self, "MoodleRDSSecurityGroup",
            vpc=vpc,
            description="Allow MySQL traffic from EC2 instances",
            allow_all_outbound=False
        )

        # Create an Application Load Balancer in the public subnet
        alb = elbv2.ApplicationLoadBalancer(self, "MoodleALB",
            vpc=vpc,
            internet_facing=True,
            load_balancer_name="MoodleALB",
            security_group=alb_security_group
        )


        # Add a listener on port 80/443 for HTTP/s traffic
        http_listener = alb.add_listener("HTTPListener",
            port=80,
            open=True
        )


        #ROLES

        # Create IAM role for the EC2 instance to enable Session Manager access
        instance_role = iam.Role(self, "MoodleInstanceRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com")
        )
        instance_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
        )
        
        # Launch a basic EC2 instance to host Moodle
        instance = ec2.Instance(self, "MoodleInstance",
            instance_type=ec2.InstanceType("t3.micro"),  # Free tier eligible
            machine_image=ec2.MachineImage.latest_amazon_linux2(),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_group=ec2_security_group,
            role=instance_role,
        )
        Tags.of(instance).add("Name", "MoodleWebServer")
        Tags.of(instance).add("Environment", "Dev")
        Tags.of(instance).add("Project", "MoodleLMS")

        # Attach the EC2 instance to the ALB target group with health check
        http_listener.add_targets("MoodleTarget",
            port=80,
            targets=[targets.InstanceTarget(instance)],
            health_check=elbv2.HealthCheck(
                path="/",
                port="80",
                healthy_http_codes="200"
            )
        )
      

        # Add a simple user data script to install Apache (to prep for Moodle)
        instance.user_data.add_commands(
            "sudo yum update -y",
            "sudo yum install -y httpd",
            "sudo systemctl enable httpd",
            "sudo systemctl start httpd",
            "echo 'OK' | sudo tee /var/www/html/index.html",
            # Install and enable the SSM agent
            "sudo yum install -y amazon-ssm-agent",
            "sudo systemctl enable amazon-ssm-agent",
            "sudo systemctl start amazon-ssm-agent"
        )

        # Create a database credentials secret for the Aurora cluster
        db_credentials_secret = rds.Credentials.from_generated_secret(
            username="moodleadmin"  # auto-generates a password and stores it in Secrets Manager
        )

        # Create an Aurora MySQL database cluster for Moodle
        db_cluster = rds.DatabaseCluster(self, "MoodleDB",
            engine=rds.DatabaseClusterEngine.aurora_mysql(
                version=rds.AuroraMysqlEngineVersion.VER_3_04_0  # Aurora MySQL version
            ),
            credentials=db_credentials_secret,
            instance_props=rds.InstanceProps(
                vpc=vpc,
                vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
                instance_type=ec2.InstanceType.of(
                    ec2.InstanceClass.BURSTABLE3,
                    ec2.InstanceSize.MEDIUM
                ),
                security_groups=[rds_security_group]  # Use RDS-specific security group
            ),
            instances=1,  # Single instance for dev
            removal_policy=RemovalPolicy.DESTROY  # Destroys DB when stack is deleted (for dev use only)
        )

        # Configure security group rules after all resources are created to avoid circular dependencies
        
        # Allow EC2 to receive traffic from ALB
        ec2_security_group.add_ingress_rule(
            ec2.Peer.security_group_id(alb_security_group.security_group_id),
            ec2.Port.tcp(80),
            "Allow HTTP traffic from ALB"
        )
        
        # Allow EC2 to receive HTTPS traffic (could be used for admin access)
        ec2_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(443),
            "Allow HTTPS traffic"
        )
        
        # Allow RDS to receive traffic from EC2
        rds_security_group.add_ingress_rule(
            ec2.Peer.security_group_id(ec2_security_group.security_group_id),
            ec2.Port.tcp(3306),
            "Allow MySQL traffic from EC2 instances"
        )
