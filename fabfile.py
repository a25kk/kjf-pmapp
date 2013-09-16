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
env.webserver = '/opt/webserver/buildout.webserver'
env.code_root = '/opt/sites/buildout.pmapp/'
env.stage_root = '/opt/sites/presshub/buildout.presshub'

env.hosts = ['pm-app', 'noah']
env.roledefs = {
    'production': ['pm-app'],
    'staging': ['noah']
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
@roles('production')
def deploy_production():
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
@roles('production')
def buildout_production():
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
@roles('production')
def deploy_full():
    """ Deploy current master to production and run buildout """
    project.site.update()
    project.site.build()
    project.cluster.restart()


@task
@roles('production')
def rebuild():
    """ Deploy current master and run full buildout """
    project.site.update()
    project.site.build_full()
    project.cluster.restart()
