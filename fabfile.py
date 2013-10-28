from fabric.api import cd
from fabric.api import env
from fabric.api import local
from fabric.api import run
from fabric.api import task
from fabric.api import roles

from ade25.fabfiles import project

env.use_ssh_config = True
env.forward_agent = True
env.port = '22222'
env.user = 'root'
env.sitename = 'pressapp'
env.code_user = 'root'
env.prod_user = 'www'
env.webserver = '/opt/sites/buildout.pressapp'
env.code_root = '/opt/sites/buildout.pressapp'
env.stage_root = '/opt/sites/mth-staging/buildout.mth'

env.hosts = ['4zu1', '4zu2', '4zu3', '6zu4']
env.roledefs = {
    'production': ['4zu1', '4zu2'],
    'public': ['4zu1'],
    'private': ['4zu2'],
    'webserver': ['4zu3'],
    'staging': ['6zu4']
}


def restart():
    """ Restart all """
    with cd(env.code_root):
        run('nice bin/supervisorctl restart all')


def restart_cluster():
    """ Restart instance """
    with cd(env.code_root):
        run('nice bin/supervisorctl restart instance1')
        run('nice bin/supervisorctl restart instance2')
        run('nice bin/supervisorctl restart instance3')
        run('nice bin/supervisorctl restart instance4')

@task
def supervisorctl(*cmd):
    """Runs an arbitrary supervisorctl command."""
    with cd(env.code_root):
        run('bin/supervisorctl ' + ' '.join(cmd))


def prepare_deploy():
    """ Push committed local changes to git """
    local('git push')


@task
@roles('staging')
def deploy_staging():
    """ Deploy current development head to staging server """
    with cd(env.stage_root):
        run('nice git pull')
    project.site.restart()


@task
@roles('private')
def deploy_private():
    """ Deploy current development head to staging server """
    with cd(env.code_root):
        run('nice git pull')
        run('nice bin/supervisorctl restart instance1')
        run('nice bin/supervisorctl restart instance2')
        run('nice bin/supervisorctl restart instance3')
        run('nice bin/supervisorctl restart instance4')


@task
@roles('public')
def deploy_public():
    """ Deploy current development head to staging server """
    with cd(env.code_root):
        run('nice git pull')
        run('nice bin/supervisorctl restart instance1')
        run('nice bin/supervisorctl restart instance2')
        run('nice bin/supervisorctl restart instance3')
        run('nice bin/supervisorctl restart instance4')


@task
@roles('staging')
def buildout_staging():
    """ Deploy current development head to staging server """
    with cd(env.stage_root):
        run('nice git pull')
    project.site.restart()


@task
@roles('private')
def buildout_private():
    """ Deploy current development head to staging server """
    with cd(env.code_root):
        run('nice git pull')
        run('nice bin/buildout -Nc deployment-server2.cfg')
        run('nice bin/supervisorctl restart instance1')
        run('nice bin/supervisorctl restart instance2')
        run('nice bin/supervisorctl restart instance3')
        run('nice bin/supervisorctl restart instance4')

@task
@roles('public')
def buildout_public():
    """ Deploy current development head to staging server """
    with cd(env.code_root):
        run('nice git pull')
        run('nice bin/buildout -Nc deployment-server1.cfg')
        run('nice bin/supervisorctl restart instance1')
        run('nice bin/supervisorctl restart instance2')
        run('nice bin/supervisorctl restart instance3')
        run('nice bin/supervisorctl restart instance4')


@task
@roles('production')
def deploy():
    """ Deploy current master to production server """
    project.site.update()
    project.cluster.restart()


@task
def deploy_full():
    """ Deploy current master to production and run buildout """
    project.site.update()
    project.site.build()
    project.cluster.restart()


@task
def rebuild():
    """ Deploy current master and run full buildout """
    project.site.update()
    project.site.build_full()
    project.cluster.restart()
fabfile.