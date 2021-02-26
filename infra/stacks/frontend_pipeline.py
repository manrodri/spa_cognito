from aws_cdk import (
    aws_codepipeline as cp,
    aws_codepipeline_actions as cp_actions,
    aws_codecommit as ccm,
    aws_codebuild as cb,
    aws_s3 as s3,
    aws_iam as iam,
    aws_ssm as ssm,
    core
)


class CodePipelineFrontendStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str , artifactbucket, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context("project_name")
        env_name = self.node.try_get_context("env")

        github_token = core.SecretValue.secrets_manager(
            secret_id=f'{env_name}/github-token', json_field='github-token'
        )

        artifact_bucket = s3.Bucket.from_bucket_name(self, 'artifact-bucket-id', bucket_name=artifactbucket)
        frontend_bucket_name = ssm.StringParameter.from_string_parameter_name(self, 'bucket-id',f"/{env_name}/frontend-bucket-name")
        # cdn_id = ssm.StringParameter.from_string_parameter_name(self, 'cdnid',
        #                                                         string_parameter_name=f'/{env_name}/cdn-id')
        # source_repo = ccm.Repository.from_repository_name(self, 'repoid', repository_name='cdk_app_frontend')



        build_project = cb.PipelineProject(self, 'buildfrontend',
                                           project_name='BuildFrontend',
                                           description='frontend project for SPA',
                                           environment=cb.BuildEnvironment(
                                               build_image=cb.LinuxBuildImage.STANDARD_3_0,
                                           ),
                                           build_spec=cb.BuildSpec.from_object({
                                               'version': '0.2',
                                               'phases': {
                                                   'pre_build': {
                                                       'commands': [
                                                           'echo Deployment started on `date`',
                                                           'echo Synching S3 Content',
                                                           f'aws s3 sync ./web/ s3://{frontend_bucket_name}'

                                                       ]
                                                   },
                                                   'build': {
                                                       'commands': [
                                                           'echo Invalidating CloudFront Cache'
                                                       ]
                                                   },
                                                   'post_build': {
                                                       'commands': [
                                                           'echo Deployment completed on  `date`'
                                                       ]
                                                   }
                                               },
                                               'artifacts': {
                                                   'files': [
                                                       '**/*'
                                                   ]
                                               }
                                           })
                                           )

        pipeline = cp.Pipeline(self, 'frontend-pipeline',
                               pipeline_name=prj_name + '-' + env_name + '-frontend-pipeline',
                               artifact_bucket=artifact_bucket,
                               restart_execution_on_update=False
                               )

        source_output = cp.Artifact(artifact_name='source')
        build_output = cp.Artifact(artifact_name='build')

        pipeline.add_stage(stage_name='Source',
                           actions=[
                               cp_actions.GitHubSourceAction(
                                   oauth_token=github_token,
                                   output=source_output,
                                   repo='spa_cognito',
                                   branch='master',
                                   owner='manrodri',
                                   action_name='GitHubSource'
                               )
                           ])

        pipeline.add_stage(stage_name='Build', actions=[
            cp_actions.CodeBuildAction(
                action_name='Build',
                input=source_output,
                project=build_project,
                outputs=[build_output]
            )
        ])

        build_project.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name('AdministratorAccess')
        )