"""
The Versioning Goat
"""

import os
import subprocess
import sys

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(PROJECT_ROOT, '..', './lib'))

from archive import Archive
from flask import Flask, request
from github import GitHub
import requests
import shutil
from StringIO import StringIO

from credentials import GITHUB_TOKEN, GITHUB_USERNAME
from config import PROJECTS


SOURCEFORGE_URL_FORMAT = "http://sourceforge.net/projects/%s/files/latest/download"
REPOS_FOLDER = os.path.join(PROJECT_ROOT, 'repos')
TMP_FOLDER = os.path.join(PROJECT_ROOT, 'tmp')


app = Flask(__name__)


def setup_repos():
    """ Ensure we have a matching GitHub repo for every import project
    """

    github = GitHub(access_token=GITHUB_TOKEN, scope='user,repo')

    current_repos = github.users(GITHUB_USERNAME).repos.get()
    repo_names = [x['name'] for x in current_repos]

    for project in PROJECTS:
        target_repo_name = 'nasa-%s' % (project['github_name'])

        if target_repo_name not in repo_names:
            github.user.repos.post(
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
        results = subprocess.check_output("git commit -m '%s'" % commit_msg,
            stderr=subprocess.STDOUT,
            shell=True)
        except subprocess.CalledProcessError:
            # assume we were already up-to-date
            return
    print results


@app.route("/ping", methods=['POST'])
def process_ping():
    """ Process an inbound ping re: a repository being updated.

    Assume ping matches format from Sendgrid:
    http://sendgrid.com/docs/API_Reference/Webhooks/parse.html
    """

    for project in PROJECTS:
        if project['name'] in request.form['subject']:
            sync_sourceforge_to_repo(project)
            break

    return "Pong"


if __name__ == "__main__":

    # Setup GitHub repos if needed
    setup_repos()

    # Start listening for pings
    app.run()
