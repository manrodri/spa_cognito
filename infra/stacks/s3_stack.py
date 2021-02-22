from aws_cdk import (
    aws_ssm as ssm,
    aws_s3 as s3,
    aws_iam as iam,
    core
)


class S3Stack(core.Stack):
    def __init__(self, app: core.App, id: str, **kwargs) -> None:
        super().__init__(app, id)

        account_id = core.Aws.ACCOUNT_ID
        prj_name = self.node.try_get_context("project_name")
        env_name = self.node.try_get_context("env")

        # pipeline artifacts bucket
        artifacts_bucket = s3.Bucket(self, 'artifact-bucket',
                                     access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL,
                                     encryption=s3.BucketEncryption.S3_MANAGED,
                                     block_public_access=s3.BlockPublicAccess(
                                         block_public_acls=True,
                                         block_public_policy=True,
                                         ignore_public_acls=True,
                                         restrict_public_buckets=True
                                     ),
                                     removal_policy=core.RemovalPolicy.DESTROY
                                     )
        core.CfnOutput(self, 's3-build-artifacts-export',
                       value=artifacts_bucket.bucket_name,
                       export_name='build-artifacts-bucket')

        ssm.StringParameter(self, 'artifacts-bucket',
                            parameter_name=f"/{env_name}/artifacts-bucket-name",
                            string_value=artifacts_bucket.bucket_name)

        # frontend bucket
        frontend_bucket = s3.Bucket(self, 'frontend',
                                     access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL,
                                     public_read_access=True,
                                     website_index_document='index.html',
                                     website_error_document='error.html',
                                     removal_policy=core.RemovalPolicy.DESTROY
                                     )

        ssm.StringParameter(self, 'frontend-bucket',
                            parameter_name=f"/{env_name}/frontend-bucket-name",
                            string_value=frontend_bucket.bucket_name)

        core.CfnOutput(self, 'frontend-bucket-export',
                       value=frontend_bucket.bucket_name,
                       export_name='frontend-bucket')



