# This script is used as CLI for run/build/deploy this service

import subprocess

import click
from typing import List

from fakeservices.fitbit_app import app as fitbitapp
from fakeservices.ihealth_app import app as ihealthapp
from fakeservices.home_app import app as homeapp

APP_CHOICE = ['fitbit', 'ihealth', 'home']

# PROJECT_ID = "p4-services"
PROJECT_ID = "data-science-258408"
IMAGE_NAME = "p4_service"
REGION = "us-central1"
IMAGE_BUILD = f"gcr.io/{PROJECT_ID}/{IMAGE_NAME}"
SERVICE_NAME_PREFIX = "p4-service"
MEM_SIZE = '512'
CPU_SIZE = '2'
CLOUD_PORT = '80'


def get_dockerfile_image_service(app_choice: str) -> List[str]:
    dockerfile = f'Dockerfile_{app_choice}'
    image = f"gcr.io/{PROJECT_ID}/{app_choice}"
    service_name = f'{SERVICE_NAME_PREFIX}-{app_choice}'
    return [dockerfile, image, service_name]


@click.group()
def cli():
    pass


@cli.command()
@click.option('--local/--container', default=True)
@click.option('-a', '--app-choice', type=click.Choice(APP_CHOICE))
def run(local: bool, app_choice: str):
    if app_choice not in APP_CHOICE:
        click.echo("Unknown app choice")
        return
    if app_choice == 'fitbit':
        app = fitbitapp
    elif app_choice == 'ihealth':
        app = ihealthapp
    elif app_choice == 'home':
        app = homeapp

    if local:
        app.debug = True
        # app.run(host='0.0.0.0', threaded=True)
        app.run(host='0.0.0.0')
    else:
        [dockerfile, image,
         service_name] = get_dockerfile_image_service(app_choice)
        run_container(image)


#         docker build --tag $ImageBuild . && docker run -it -p 5000:80 $ImageBuild
# gcloud builds submit --tag gcr.io/$ProjectID/$ImageName
@cli.command()
@click.option('--local/--cloud', default=True)
@click.option('--run', is_flag=True, default=False)
@click.option('--deploy', is_flag=True, default=False)
@click.option('-a', '--app-choice', type=click.Choice(APP_CHOICE))
def build(local: bool, run: bool, deploy: bool, app_choice: str):
    [dockerfile, image,
     service_name] = get_dockerfile_image_service(app_choice)
    if local:
        build_local(dockerfile, image)
    else:
        build_gcloud()

    if run:
        run_container(image)

    if deploy:
        deploy_gcloud(image, service_name)


#        docker push $ImageBuild
#        gcloud run deploy $ServiceName --platform managed --region $Region --image $ImageBuild
@cli.command()
@click.option('-a', '--app-choice', type=click.Choice(APP_CHOICE))
def deploy(app_choice: str):
    [dockerfile, image,
     service_name] = get_dockerfile_image_service(app_choice)
    deploy_gcloud(image, service_name)


def run_container(image: str):
    print('Running image')
    subprocess.run(['docker', 'run', '-it', '-p', '5000:80', image])


def build_local(dockerfile: str, image: str):
    print('Building image locally')
    subprocess.run(['docker', 'build', '-f', dockerfile, '--tag', image, '.'])


def build_gcloud():
    print('Building image in Google Cloud Build')
    subprocess.run(['gcloud', 'builds', 'submit', '--tag', IMAGE_BUILD])


def deploy_gcloud(image: str, service_name: str):
    print('Deploying image')
    subprocess.run(['docker', 'push', image])
    subprocess.run([
        'gcloud', 'run', 'deploy', service_name, '--platform', 'managed',
        '--region', REGION, '--image', image, '--memory', MEM_SIZE, '--port',
        CLOUD_PORT
    ])


# MODEL_PATH = "models"
# BUCKET = "data-science-258408-skin-lesion-cls-models"
# MODEL_CLOUD = "models/dense161.pth.tar"
#
# # gsutil cp $ModelPath gs://$Bucket/$ModelCloud
# # https://storage.cloud.google.com/data-science-258408-skin-lesion-cls-models/models/dense161.pth.tar
# @cli.command()
# @click.argument('model', type=click.Path(exists=True))
# def upload(model: str):
#     pass

if __name__ == '__main__':
    cli()
