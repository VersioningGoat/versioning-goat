"""
The Versioning Goat
"""

import os
import subprocess
import sys
import indicator

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(PROJECT_ROOT, '..', './lib'))

from archive import Archive
from flask import Flask, request
from github import GitHub
import requests
import shutil
from StringIO import StringIO

from credentials import GITHUB_TOKEN, GITHUB_ORGANIZATION, MAIL
from config import PROJECTS


SOURCEFORGE_URL_FORMAT = "http://sourceforge.net/projects/%s/files/latest/download"  # % project['sourceforge_name']
GITHUB_REPO_URL_FORMAT = "git@github.com:%s/%s.git"  # % (GITHUB_ORGANIZATION, project['github_name'])

# Prefix we add to every repo we create and sync to:
GITHUB_REPO_NAME_FORMAT = "nasa-%s"  # % project['github_name']"

REPOS_FOLDER = os.path.join(PROJECT_ROOT, 'repos')
TMP_FOLDER = os.path.join(PROJECT_ROOT, 'tmp')


app = Flask(__name__)


# Set up logging
import logging
from logging import Formatter
from logging.handlers import SMTPHandler
formatter = Formatter('''
    Message type:       %(levelname)s
    Location:           %(pathname)s:%(lineno)d
    Module:             %(module)s
    Function:           %(funcName)s
    Time:               %(asctime)s

    Message:

    %(message)s
''')
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)
app.logger.addHandler(stream_handler)
app.logger.setLevel(logging.DEBUG)

if (not app.debug and 'smtp_password' in MAIL
        and MAIL['smtp_password'] is not None):
    mail_handler = SMTPHandler(MAIL['smtp_host'],
                           'server-error@example.com',
                           MAIL['mailto'], 'Versioning Goat Fail',
                           (MAIL['smtp_user'], MAIL['smtp_password']),
                           secure=True)
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(formatter)
    app.logger.addHandler(mail_handler)


def setup_repos():
    """ Ensure we have a matching GitHub repo for every import project
    """

    github = GitHub(access_token=GITHUB_TOKEN, scope='user,repo')

    #current_repos = github.users(GITHUB_USERNAME).repos.get()
    current_repos = github.orgs(GITHUB_ORGANIZATION).repos.get()

    repo_names = [x['name'] for x in current_repos]

    for project in PROJECTS:
        target_repo_name = GITHUB_REPO_NAME_FORMAT % (project['github_name'])

        if target_repo_name not in repo_names:
            github.orgs(GITHUB_ORGANIZATION).repos.post(
                name=target_repo_name,
                description='Mirrored repository')  # FIXME


def retrieve_file(url):
    """ Retrieve a remote file and return a file-like object for it

        In: `url`
        Out: file-like object
    """
    response = requests.get(url)

    filelike = StringIO(response.content)

    # augment with filename so Archive and other packages know how to handle
    filelike.name = response.url.split('/')[-1]

    # TODO: use content-type header to generate filename
    #   if we don't get good name from server.
    # content_type = response.headers['content-type']

    return filelike


def sync_sourceforge_to_repo(project):
    download_url = SOURCEFORGE_URL_FORMAT % (project['sourceforge_name'])

    response = retrieve_file(download_url)

    tmp_folder = project_tmp = os.path.join(TMP_FOLDER, project['github_name'])
    Archive(response).extract(tmp_folder)

    # Remove everything in local repo except for .git folder, we'll
    #   be replacing everything with archive contents and letting git
    #   worry about tracking changes.
    # TODO: solid sanity check needed here before we rmtree a bunch
    #   of stuff...
    project_repo = os.path.join(REPOS_FOLDER, project['github_name'])
    try:
        os.mkdir(project_repo)
    except OSError:
        pass
    os.chdir(project_repo)
    os.system('git init')
    remote_name = GITHUB_REPO_NAME_FORMAT % project['github_name']
    os.system('git remote add origin ' +
            GITHUB_REPO_URL_FORMAT % (GITHUB_ORGANIZATION, remote_name))
    for item in os.listdir(project_repo):
        if item == '.git':
            continue
        if os.path.isdir(item):
            shutil.rmtree(item)
        else:
            os.remove(item)

    # If we extracted a directory, copy out its contents,
    #   we're not interested in the directory:
    os.chdir(tmp_folder)
    extracted_files = os.listdir(tmp_folder)
    if len(extracted_files) == 1 and os.path.isdir(extracted_files[0]):
        tmp_folder = os.path.join(tmp_folder, extracted_files[0])
        os.chdir(tmp_folder)

    for item in os.listdir(tmp_folder):
        if item == '.git':
            continue
        shutil.move(item, project_repo)

    # We're done with the tmp folder, do cleanup
    shutil.rmtree(project_tmp)

    os.chdir(project_repo)

    results = subprocess.check_output("git add *",
        stderr=subprocess.STDOUT,
        shell=True)
    print results

    commit_msg = "Automatic update from package"

    # Time to commit any changes to git!
    try:
        results = subprocess.check_output("git commit -am '%s'" % commit_msg,
            stderr=subprocess.STDOUT,
            shell=True)
    except subprocess.CalledProcessError:
        # assume we were already up-to-date
        pass
    else:
        print results

    results = subprocess.check_output("git push origin master",
            stderr=subprocess.STDOUT,
            shell=True)


@app.route("/ping", methods=['POST'])
def process_ping():
    """ Process an inbound ping re: a repository being updated.

    Assume ping matches format from Sendgrid:
    http://sendgrid.com/docs/API_Reference/Webhooks/parse.html
    """

    import pprint
    app.logger.debug(pprint.pformat(request.form))

    for project in PROJECTS:
        if project['name'] in request.form['subject']:
            sync_sourceforge_to_repo(project)
            break

    return "Pong"


@app.route("/status", methods=['GET'])
def get_image():
    return indicator.get_image(request)

if __name__ == "__main__":

    # Setup GitHub repos if needed
    setup_repos()

    # Start listening for pings
    app.debug = True
    app.run()
