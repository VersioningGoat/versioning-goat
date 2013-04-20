from flask import Flask, request
import magic
import re
import requests

"""
Format for snapshot request URL:
https://sourceforge.net/p/djangoajaxcl/code/1/tarball

Format for (SVN) code snapshots:
http://sourceforge.net/code-snapshots/svn/d/dj/djangoajaxcl/code/djangoajaxcl-code-2.tar.gz

where 2 is revision name

wget http://sourceforge.net/projects/phppgadmin/files/latest/download
"""


SOURCEFORGE_URL_FORMAT = "http://sourceforge.net/projects/%s/files/latest/download"

app = Flask(__name__)

projects = {
        'Sync, Archive, Validate, Exchange': {
            'short_name': 'save-ha'
         }
}


def retrieve_archive(url):
    response = requests.get(url)
    return response.content


@app.route("/ping", methods=['POST'])
def process_ping():
    """ We've just been pinged that a repository has been updated.

    Assume ping matches format from Sendgrid:
    http://sendgrid.com/docs/API_Reference/Webhooks/parse.html
    """

    for projectname, data in projects.iteritems():
        if projectname in request.form['subject']:
            download_url = SOURCEFORGE_URL_FORMAT % (data['short_name'])
            response = retrieve_archive(download_url)
            # TODO: extract response archive, add new remote and Github repo
            #    if needed, push
            break

if __name__ == "__main__":
    app.run()
