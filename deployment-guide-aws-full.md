# ☁️ VelocityIQ Deployment Guide: AWS Full Stack

## **Option 2: AWS Enterprise Deployment (Production Scale)**

### **Architecture Overview**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CloudFront    │    │   Application   │    │   RDS/Supabase  │
│   + S3 Bucket   │───▶│   Load Balancer │───▶│   PostgreSQL    │
│   (Frontend)    │    │   + ECS/Fargate │    │   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   SageMaker     │
                       │   Endpoints     │
                       └─────────────────┘
```

---

## 🚀 **Step 1: Frontend - S3 + CloudFront**

### **1.1 Build Production Frontend**
```bash
cd dashboard
npm run build

# Install AWS CLI if not already installed
aws configure
```

### **1.2 Create S3 Bucket for Static Hosting**
```bash
# Create bucket (replace with unique name)
aws s3 mb s3://velocityiq-dashboard-frontend

# Enable static website hosting
aws s3 website s3://velocityiq-dashboard-frontend \
    --index-document index.html \
    --error-document index.html

# Upload build files
aws s3 sync build/ s3://velocityiq-dashboard-frontend --delete

# Set public read permissions
aws s3api put-bucket-policy --bucket velocityiq-dashboard-frontend --policy '{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::velocityiq-dashboard-frontend/*"
        }
    ]
}'
```

### **1.3 Create CloudFormation Template for CloudFront**
Create `aws-frontend-stack.yaml`:
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'VelocityIQ Frontend Distribution'

Parameters:
  S3BucketName:
    Type: String
    Default: velocityiq-dashboard-frontend
  
  APIGatewayDomain:
    Type: String
    Description: Domain of the backend API
    Default: your-api-gateway-domain.amazonaws.com

Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          - Id: S3Origin
            DomainName: !Sub "${S3BucketName}.s3-website-${AWS::Region}.amazonaws.com"
            CustomOriginConfig:
              HTTPPort: 80
              HTTPSPort: 443
              OriginProtocolPolicy: http-only
        Enabled: true
        DefaultRootObject: index.html
        DefaultCacheBehavior:
          TargetOriginId: S3Origin
          ViewerProtocolPolicy: redirect-to-https
          CachePolicyId: 4135ea2d-6df8-44a3-9df3-4b5a84be39ad  # Managed-CachingDisabled
        PriceClass: PriceClass_100
        HttpVersion: http2
        CustomErrorResponses:
          - ErrorCode: 404
            ResponseCode: 200
            ResponsePagePath: /index.html
          - ErrorCode: 403
            ResponseCode: 200
            ResponsePagePath: /index.html

Outputs:
  DistributionDomainName:
    Description: CloudFront Distribution Domain Name
    Value: !GetAtt CloudFrontDistribution.DomainName
    Export:
      Name: !Sub "${AWS::StackName}-DistributionDomain"
```

Deploy:
```bash
aws cloudformation deploy --template-file aws-frontend-stack.yaml \
    --stack-name velocityiq-frontend \
    --parameter-overrides S3BucketName=velocityiq-dashboard-frontend
```

---

## 🔥 **Step 2: Backend - ECS Fargate + Application Load Balancer**

### **2.1 Create Dockerfile**
Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements_dashboard.txt .
RUN pip install --no-cache-dir -r requirements_dashboard.txt

# Copy application code
COPY dashboard_api_fixed.py .
COPY supabase_forecasting_integration.py .
COPY *.py .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run application
CMD ["uvicorn", "dashboard_api_fixed:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **2.2 Build and Push to ECR**
```bash
# Create ECR repository
aws ecr create-repository --repository-name velocityiq-backend

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build Docker image
docker build -t velocityiq-backend .

# Tag and push
docker tag velocityiq-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/velocityiq-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/velocityiq-backend:latest
```

### **2.3 Create ECS Infrastructure**
Create `aws-backend-stack.yaml`:
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'VelocityIQ Backend ECS Infrastructure'

Parameters:
  VpcId:
    Type: AWS::EC2::VPC::Id
    Description: VPC ID for the infrastructure
  
  SubnetIds:
    Type: List<AWS::EC2::Subnet::Id>
    Description: List of subnet IDs
  
  ImageUri:
    Type: String
    Description: ECR Image URI
    Default: <account-id>.dkr.ecr.us-east-1.amazonaws.com/velocityiq-backend:latest

Resources:
  # ECS Cluster
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: velocityiq-cluster
      CapacityProviders:
        - FARGATE
      DefaultCapacityProviderStrategy:
        - CapacityProvider: FARGATE
          Weight: 1

  # Application Load Balancer
  ALB:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: velocityiq-alb
      Scheme: internet-facing
      Type: application
      Subnets: !Ref SubnetIds
      SecurityGroups:
        - !Ref ALBSecurityGroup

  ALBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for ALB
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0

  # Target Group
  TargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: velocityiq-tg
      Port: 8000
      Protocol: HTTP
      VpcId: !Ref VpcId
      TargetType: ip
      HealthCheckPath: /
      HealthCheckIntervalSeconds: 30
      HealthCheckTimeoutSeconds: 5
      HealthyThresholdCount: 2
      UnhealthyThresholdCount: 5

  # ALB Listener
  ALBListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref TargetGroup
      LoadBalancerArn: !Ref ALB
      Port: 80
      Protocol: HTTP

  # ECS Task Definition
  TaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: velocityiq-backend
      Cpu: 512
      Memory: 1024
      NetworkMode: awsvpc
      RequiresCompatibilities:
        - FARGATE
      ExecutionRoleArn: !Ref ExecutionRole
      TaskRoleArn: !Ref TaskRole
      ContainerDefinitions:
        - Name: velocityiq-backend
          Image: !Ref ImageUri
          PortMappings:
            - ContainerPort: 8000
              Protocol: tcp
          Environment:
            - Name: SUPABASE_URL
              Value: !Ref SupabaseUrl
            - Name: SUPABASE_KEY
              Value: !Ref SupabaseKey
            - Name: AWS_DEFAULT_REGION
              Value: !Ref AWS::Region
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref LogGroup
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: ecs

  # ECS Service
  ECSService:
    Type: AWS::ECS::Service
    DependsOn: ALBListener
    Properties:
      ServiceName: velocityiq-service
      Cluster: !Ref ECSCluster
      TaskDefinition: !Ref TaskDefinition
      DesiredCount: 2
      LaunchType: FARGATE
      NetworkConfiguration:
        AwsvpcConfiguration:
          SecurityGroups:
            - !Ref ECSSecurityGroup
          Subnets: !Ref SubnetIds
          AssignPublicIp: ENABLED
      LoadBalancers:
        - ContainerName: velocityiq-backend
          ContainerPort: 8000
          TargetGroupArn: !Ref TargetGroup

  # ECS Security Group
  ECSSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for ECS tasks
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 8000
          ToPort: 8000
          SourceSecurityGroupId: !Ref ALBSecurityGroup

  # IAM Roles
  ExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

  TaskRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: SageMakerAccess
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - sagemaker:InvokeEndpoint
                  - sagemaker:DescribeEndpoint
                Resource: '*'

  # CloudWatch Log Group
  LogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: /ecs/velocityiq-backend
      RetentionInDays: 7

Parameters:
  SupabaseUrl:
    Type: String
    Description: Supabase URL
    NoEcho: true
  
  SupabaseKey:
    Type: String
    Description: Supabase API Key
    NoEcho: true

Outputs:
  LoadBalancerDNS:
    Description: DNS name of the load balancer
    Value: !GetAtt ALB.DNSName
    Export:
      Name: !Sub "${AWS::StackName}-LoadBalancerDNS"
```

Deploy:
```bash
aws cloudformation deploy --template-file aws-backend-stack.yaml \
    --stack-name velocityiq-backend \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides \
        VpcId=vpc-xxxxxxxx \
        SubnetIds=subnet-xxxxxxxx,subnet-yyyyyyyy \
        ImageUri=<account-id>.dkr.ecr.us-east-1.amazonaws.com/velocityiq-backend:latest \
        SupabaseUrl=https://your-project.supabase.co \
        SupabaseKey=your-supabase-key
```

---

## 🔧 **Step 3: Auto Scaling & Monitoring**

### **3.1 Add Auto Scaling**
Create `autoscaling.yaml`:
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Auto Scaling for VelocityIQ'

Parameters:
  ECSClusterName:
    Type: String
    Default: velocityiq-cluster
  
  ECSServiceName:
    Type: String
    Default: velocityiq-service

Resources:
  # Auto Scaling Target
  ScalableTarget:
    Type: AWS::ApplicationAutoScaling::ScalableTarget
    Properties:
      ServiceNamespace: ecs
      ResourceId: !Sub "service/${ECSClusterName}/${ECSServiceName}"
      ScalableDimension: ecs:service:DesiredCount
      MinCapacity: 2
      MaxCapacity: 10
      RoleARN: !Sub "arn:aws:iam::${AWS::AccountId}:role/aws-service-role/ecs.application-autoscaling.amazonaws.com/AWSServiceRoleForApplicationAutoScaling_ECSService"

  # CPU Scaling Policy
  CPUScalingPolicy:
    Type: AWS::ApplicationAutoScaling::ScalingPolicy
    Properties:
      PolicyName: CPUScalingPolicy
      PolicyType: TargetTrackingScaling
      ServiceNamespace: ecs
      ResourceId: !Ref ScalableTarget
      ScalableDimension: ecs:service:DesiredCount
      TargetTrackingScalingPolicyConfiguration:
        TargetValue: 70
        PredefinedMetricSpecification:
          PredefinedMetricType: ECSServiceAverageCPUUtilization
        ScaleOutCooldown: 300
        ScaleInCooldown: 300

  # Memory Scaling Policy
  MemoryScalingPolicy:
    Type: AWS::ApplicationAutoScaling::ScalingPolicy
    Properties:
      PolicyName: MemoryScalingPolicy
      PolicyType: TargetTrackingScaling
      ServiceNamespace: ecs
      ResourceId: !Ref ScalableTarget
      ScalableDimension: ecs:service:DesiredCount
      TargetTrackingScalingPolicyConfiguration:
        TargetValue: 80
        PredefinedMetricSpecification:
          PredefinedMetricType: ECSServiceAverageMemoryUtilization
        ScaleOutCooldown: 300
        ScaleInCooldown: 300
```

### **3.2 Set Up CloudWatch Alarms**
```bash
# High CPU Alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "VelocityIQ-HighCPU" \
    --alarm-description "Alarm when CPU exceeds 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/ECS \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2

# High Memory Alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "VelocityIQ-HighMemory" \
    --alarm-description "Alarm when Memory exceeds 85%" \
    --metric-name MemoryUtilization \
    --namespace AWS/ECS \
    --statistic Average \
    --period 300 \
    --threshold 85 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2
```

---

## 🚀 **Step 4: CI/CD Pipeline**

### **4.1 Create CodePipeline**
Create `cicd-pipeline.yaml`:
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'CI/CD Pipeline for VelocityIQ'

Parameters:
  GitHubOwner:
    Type: String
    Description: GitHub repository owner
  
  GitHubRepo:
    Type: String
    Description: GitHub repository name
    Default: VelocityIQ
  
  GitHubToken:
    Type: String
    Description: GitHub personal access token
    NoEcho: true

Resources:
  # S3 Bucket for Pipeline Artifacts
  ArtifactsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "velocityiq-pipeline-artifacts-${AWS::AccountId}"
      VersioningConfiguration:
        Status: Enabled

  # CodeBuild Project for Backend
  BackendBuildProject:
    Type: AWS::CodeBuild::Project
    Properties:
      Name: velocityiq-backend-build
      ServiceRole: !Ref CodeBuildRole
      Artifacts:
        Type: CODEPIPELINE
      Environment:
        Type: LINUX_CONTAINER
        ComputeType: BUILD_GENERAL1_MEDIUM
        Image: aws/codebuild/standard:5.0
        PrivilegedMode: true
      Source:
        Type: CODEPIPELINE
        BuildSpec: |
          version: 0.2
          phases:
            pre_build:
              commands:
                - echo Logging in to Amazon ECR...
                - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
            build:
              commands:
                - echo Build started on `date`
                - echo Building the Docker image...
                - docker build -t $IMAGE_REPO_NAME:$IMAGE_TAG .
                - docker tag $IMAGE_REPO_NAME:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG
            post_build:
              commands:
                - echo Build completed on `date`
                - echo Pushing the Docker image...
                - docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG
                - echo Writing image definitions file...
                - printf '[{"name":"velocityiq-backend","imageUri":"%s"}]' $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG > imagedefinitions.json
          artifacts:
            files: imagedefinitions.json

  # CodeBuild Project for Frontend
  FrontendBuildProject:
    Type: AWS::CodeBuild::Project
    Properties:
      Name: velocityiq-frontend-build
      ServiceRole: !Ref CodeBuildRole
      Artifacts:
        Type: CODEPIPELINE
      Environment:
        Type: LINUX_CONTAINER
        ComputeType: BUILD_GENERAL1_MEDIUM
        Image: aws/codebuild/standard:5.0
      Source:
        Type: CODEPIPELINE
        BuildSpec: |
          version: 0.2
          phases:
            pre_build:
              commands:
                - echo Installing dependencies...
                - cd dashboard && npm install
            build:
              commands:
                - echo Building the React app...
                - REACT_APP_API_URL=$REACT_APP_API_URL npm run build
            post_build:
              commands:
                - echo Uploading to S3...
                - aws s3 sync build/ s3://$S3_BUCKET --delete
                - echo Creating CloudFront invalidation...
                - aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_DISTRIBUTION_ID --paths "/*"

  # CodePipeline
  Pipeline:
    Type: AWS::CodePipeline::Pipeline
    Properties:
      Name: velocityiq-pipeline
      RoleArn: !Ref CodePipelineRole
      ArtifactStore:
        Type: S3
        Location: !Ref ArtifactsBucket
      Stages:
        - Name: Source
          Actions:
            - Name: SourceAction
              ActionTypeId:
                Category: Source
                Owner: ThirdParty
                Provider: GitHub
                Version: 1
              Configuration:
                Owner: !Ref GitHubOwner
                Repo: !Ref GitHubRepo
                Branch: main
                OAuthToken: !Ref GitHubToken
              OutputArtifacts:
                - Name: SourceOutput

        - Name: Build
          Actions:
            - Name: BackendBuild
              ActionTypeId:
                Category: Build
                Owner: AWS
                Provider: CodeBuild
                Version: 1
              Configuration:
                ProjectName: !Ref BackendBuildProject
                EnvironmentVariables: |
                  [
                    {"name":"AWS_DEFAULT_REGION","value":"us-east-1"},
                    {"name":"AWS_ACCOUNT_ID","value":"${AWS::AccountId}"},
                    {"name":"IMAGE_REPO_NAME","value":"velocityiq-backend"},
                    {"name":"IMAGE_TAG","value":"latest"}
                  ]
              InputArtifacts:
                - Name: SourceOutput
              OutputArtifacts:
                - Name: BackendBuildOutput
              RunOrder: 1

            - Name: FrontendBuild
              ActionTypeId:
                Category: Build
                Owner: AWS
                Provider: CodeBuild
                Version: 1
              Configuration:
                ProjectName: !Ref FrontendBuildProject
                EnvironmentVariables: |
                  [
                    {"name":"S3_BUCKET","value":"velocityiq-dashboard-frontend"},
                    {"name":"CLOUDFRONT_DISTRIBUTION_ID","value":"${CloudFrontDistributionId}"},
                    {"name":"REACT_APP_API_URL","value":"https://${ALBDNSName}"}
                  ]
              InputArtifacts:
                - Name: SourceOutput
              RunOrder: 1

        - Name: Deploy
          Actions:
            - Name: BackendDeploy
              ActionTypeId:
                Category: Deploy
                Owner: AWS
                Provider: ECS
                Version: 1
              Configuration:
                ClusterName: velocityiq-cluster
                ServiceName: velocityiq-service
                FileName: imagedefinitions.json
              InputArtifacts:
                - Name: BackendBuildOutput
              RunOrder: 1

  # IAM Roles
  CodeBuildRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: codebuild.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: CodeBuildPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - logs:CreateLogGroup
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                  - ecr:BatchCheckLayerAvailability
                  - ecr:GetDownloadUrlForLayer
                  - ecr:BatchGetImage
                  - ecr:GetAuthorizationToken
                  - s3:GetObject
                  - s3:PutObject
                  - s3:GetBucketLocation
                  - s3:ListBucket
                  - cloudfront:CreateInvalidation
                Resource: '*'

  CodePipelineRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: codepipeline.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: CodePipelinePolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:PutObject
                  - s3:GetBucketLocation
                  - s3:ListBucket
                  - codebuild:BatchGetBuilds
                  - codebuild:StartBuild
                  - ecs:DescribeServices
                  - ecs:DescribeTaskDefinition
                  - ecs:DescribeTasks
                  - ecs:ListTasks
                  - ecs:RegisterTaskDefinition
                  - ecs:UpdateService
                  - iam:PassRole
                Resource: '*'
```

---

## 💰 **Cost Estimation (AWS Full Stack)**

### **Monthly Costs (Production Load)**
- **ECS Fargate**: ~$50-100/month (2-4 tasks)
- **Application Load Balancer**: ~$20/month
- **CloudFront**: ~$10-30/month
- **S3 Storage**: ~$5/month
- **RDS/Supabase**: ~$50-200/month
- **SageMaker Endpoints**: ~$50-150/month
- **CloudWatch Logs**: ~$10/month

**Total: ~$195-515/month**

---

## 🔒 **Security Best Practices**

### **Network Security**
```bash
# VPC Security Groups
aws ec2 create-security-group \
    --group-name velocityiq-sg \
    --description "VelocityIQ Security Group" \
    --vpc-id vpc-xxxxxxxx

# Restrict access to specific IPs
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxx \
    --protocol tcp \
    --port 443 \
    --cidr 10.0.0.0/8
```

### **Secrets Management**
```bash
# Store secrets in AWS Secrets Manager
aws secretsmanager create-secret \
    --name "velocityiq/supabase" \
    --description "Supabase credentials" \
    --secret-string '{"url":"https://your-project.supabase.co","key":"your-key"}'

# Store SageMaker endpoint details
aws secretsmanager create-secret \
    --name "velocityiq/sagemaker" \
    --description "SageMaker endpoint configuration" \
    --secret-string '{"endpoint_name":"chronos-endpoint","region":"us-east-1"}'
```

### **IAM Policies**
Create least-privilege IAM roles for each service component.

---

## 📊 **Monitoring & Observability**

### **Application Monitoring**
```bash
# Install CloudWatch Agent
# Add to Dockerfile:
RUN wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
RUN rpm -U ./amazon-cloudwatch-agent.rpm
```

### **Custom Metrics**
```python
# Add to your FastAPI app
import boto3
cloudwatch = boto3.client('cloudwatch')

def put_custom_metric(metric_name, value, unit='Count'):
    cloudwatch.put_metric_data(
        Namespace='VelocityIQ/Application',
        MetricData=[
            {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit
            }
        ]
    )
```

---

**🎉 You now have an enterprise-grade AWS deployment for VelocityIQ!**

This setup provides:
- ✅ **High Availability**: Multi-AZ deployment
- ✅ **Auto Scaling**: Based on CPU/Memory metrics  
- ✅ **Security**: VPC, Security Groups, IAM roles
- ✅ **Monitoring**: CloudWatch, custom metrics
- ✅ **CI/CD**: Automated deployments
- ✅ **Cost Optimization**: Right-sized resources 