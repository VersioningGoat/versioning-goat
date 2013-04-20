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

"""
POSSIBLE INPUTS:

* URL of static package.  We just assume this always refers to the latest version and pull
    in periodically.  e.g. http://opensource.gsfc.nasa.gov/projects/DQSS/dqss_64.tar
* Sourceforge file archive.  We get pinged re: when to update via their email notifications
* Sourceforge repo (probably ignore this use case, NASA projects don't seem to use)
* Third-party SVN

Format for snapshot request URL:
https://sourceforge.net/p/djangoajaxcl/code/1/tarball

Format for (SVN) code snapshots:
http://sourceforge.net/code-snapshots/svn/d/dj/djangoajaxcl/code/djangoajaxcl-code-2.tar.gz

where 2 is revision name

wget http://sourceforge.net/projects/phppgadmin/files/latest/download
"""


SOURCEFORGE_URL_FORMAT = "http://sourceforge.net/projects/%s/files/latest/download"
REPOS_FOLDER = os.path.join(PROJECT_ROOT, '/repos')


app = Flask(__name__)

projects = {
        'Sync, Archive, Validate, Exchange': {
            'short_name': 'save-ha'
         }
}

def setup_repos():
    """
    """

    github = GitHub(access_token=GITHUB_TOKEN, scope='user,repo')

    for name, data in projects.iteritems():
        github.user.repos.post(
            name='nasa-%s' % (data['short_name']),
            description='Mirrored repository')


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

    for projectname, data in projects.iteritems():
        if projectname in request.form['subject']:
            download_url = SOURCEFORGE_URL_FORMAT % (data['short_name'])
            response = retrieve_file(download_url)

            # extract to current dir
            Archive(response).extract(REPOS_FOLDER)
            # TODO: extract response archive, add new remote and Github repo
            #    if needed, push
            break

if __name__ == "__main__":
    app.run()
