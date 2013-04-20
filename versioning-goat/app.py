"""
Edward The Versioning Goat
"""

PROJECTS = {
        'Sync, Archive, Validate, Exchange': {
            'short_name': 'save-ha'
         }
}


import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(PROJECT_ROOT, '..', './lib'))

from archive import Archive
from flask import Flask, request
from github import GitHub
import requests
from StringIO import StringIO

from credentials import GITHUB_TOKEN, GITHUB_USERNAME


SOURCEFORGE_URL_FORMAT = "http://sourceforge.net/projects/%s/files/latest/download"
REPOS_FOLDER = os.path.join(PROJECT_ROOT, '/repos')


app = Flask(__name__)


def setup_repos():
    """ Ensure we have a matching GitHub repo for every import project
    """

    github = GitHub(access_token=GITHUB_TOKEN, scope='user,repo')

    current_repos = github.users(GITHUB_USERNAME).repos.get()
    repo_names = [x['name'] for x in current_repos]

    for name, data in PROJECTS.iteritems():
        target_repo_name = 'nasa-%s' % (data['short_name'])

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


@app.route("/ping", methods=['POST'])
def process_ping():
    """ Process an inbound ping re: a repository being updated.

    Assume ping matches format from Sendgrid:
    http://sendgrid.com/docs/API_Reference/Webhooks/parse.html
    """

    for projectname, data in PROJECTS.iteritems():
        if projectname in request.form['subject']:
            download_url = SOURCEFORGE_URL_FORMAT % (data['short_name'])
            response = retrieve_file(download_url)

            # extract to current dir
            Archive(response).extract(REPOS_FOLDER)
            # TODO: extract response archive, add new remote and Github repo
            #    if needed, push
            break

if __name__ == "__main__":

    # Setup GitHub repos if needed
    setup_repos()

    # Start listening for pings
    app.run()
