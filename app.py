from flask import Flask, request
import re

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
        'Polar Explorer': {
            'short_name': 'djangoajaxcl'
         }
}


@app.route("/ping", methods=['POST'])
def process_ping():
    """ We've just been pinged that a repository has been updated.

    Assume ping is always from Sendgrid and matches the format:
    http://sendgrid.com/docs/API_Reference/Webhooks/parse.html
    """

    for projectname in projects:
        if projectname in request.form['subject']:
            project = projects[projectname]
            download_url = SOURCEFORGE_URL_FORMAT % (project['short_name'])

if __name__ == "__main__":
    app.run()
