from aws_cdk import (
    aws_route53 as r53,
    aws_route53_targets as r53targets,
    aws_s3 as s3,
    aws_iam as iam,
    aws_cloudfront as cdn,
    aws_ssm as ssm,
    core
)


class DnsStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        account_id = core.Aws.ACCOUNT_ID
        prj_name = self.node.try_get_context("project_name")
        env_name = self.node.try_get_context("env")

        frontend_bucket_name = ssm.StringParameter.from_string_parameter_name(self,
                                                                              'bucket-id',
                                                                              f"/{env_name}/frontend-bucket-name")
        webhosting_bucket = s3.Bucket.from_bucket_name(self, 'webhosting-id',
                                                       bucket_name=frontend_bucket_name.string_value)

        hosted_zone = r53.HostedZone.from_lookup(self, 'hosted-zone-id',
                                                 domain_name='manrodri.com')

        # cname = r53.CnameRecord(self, 'cname_record',
        #                         zone=hosted_zone,
        #                         record_name='example',
        #                         domain_name=webhosting_bucket.bucket_website_domain_name)


        r53.ARecord(self, 'cdn-record',
                    zone=hosted_zone,
                    target=r53.RecordTarget.from_alias(alias_target=r53targets.BucketWebsiteTarget(webhosting_bucket)),
                    record_name='example'
                    )



        # arecord = r53.RecordTarget.from_alias(r53targets.BucketWebsiteTarget(webhosting_bucket))

        ssm.StringParameter(self, 'zone-id',
                            parameter_name='/' + env_name + '/zone-id',
                            string_value=hosted_zone.hosted_zone_id
                            )
