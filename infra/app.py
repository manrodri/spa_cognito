#!/usr/bin/env python3
from aws_cdk import core

from stacks.s3_stack import S3Stack

app = core.App()
S3Stack(app, "s3-stack", env={'region': 'eu-west-1'})


app.synth()
