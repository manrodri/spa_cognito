#!/usr/bin/env python3
from aws_cdk import core

from stacks.s3_stack import S3Stack
from stacks.frontend_pipeline import CodePipelineFrontendStack
from stacks.dns_stack import DnsStack

app = core.App()
s3_stack = S3Stack(app, "s3-stack", env={'region': 'eu-west-1'})
frontend_pipeline_stack = CodePipelineFrontendStack(app, 'frontend-pipeline-stack',
                                                    artifactbucket=core.Fn.import_value('build-artifacts-bucket'),
                                                    env={'region': 'eu-west-1'})
dns_stack = DnsStack(app, 'dns-stack',  env={'region': 'eu-west-1', 'account': '113568932124'})




app.synth()
