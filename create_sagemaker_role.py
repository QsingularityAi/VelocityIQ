import boto3
import json

def create_sagemaker_role(role_name="SageMakerExecutionRole"):
    iam = boto3.client("iam")

    assume_role_policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "sagemaker.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }

    try:
        create_role_response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_role_policy_document),
        )
        role_arn = create_role_response["Role"]["Arn"]
        print(f"Created role {role_name} with ARN: {role_arn}")
    except iam.exceptions.EntityAlreadyExistsException:
        print(f"Role {role_name} already exists, retrieving ARN.")
        role_arn = iam.get_role(RoleName=role_name)["Role"]["Arn"]

    policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
    iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
    print(f"Attached policy {policy_arn} to role {role_name}")

    with open("sagemaker_role.json", "w") as f:
        json.dump({"role_arn": role_arn}, f)
    print("SageMaker role ARN saved to sagemaker_role.json")

if __name__ == "__main__":
    create_sagemaker_role()
