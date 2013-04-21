from flask import send_file
from config import PROJECTS
import app
import requests


def get_image(request):
    # Checks for repos with push enables (aka SourceForge)
    if request.args.get('sync_method') == 'push':
        filename = '../assets/images/goat_ok.png'
        return send_file(filename, mimetype='image/png', add_etags=False)
    # Checks for goat-loving static files
    check = up_to_date(request.args.get('repo_url'), request.args.get('etag'))
    if check is True:
        filename = '../assets/images/goat_ok.png'
    elif check is False:
        filename = '../assets/images/goat_work.png'
        for project in PROJECTS:
            if project['url'] in request.args.get('repo_url'):
                # TODO: Thread this thing out!
                app.sync_sourceforge_to_repo(project)
                break
    else:
        filename = '../assets/images/goat_error.png'
    return send_file(filename, mimetype='image/png', add_etags=False)


def up_to_date(repo_url, etag):
    if repo_url and etag:
        new_etag = requests.head(repo_url, headers={"content-type": "text"}).headers['etag']
        if etag == new_etag:
            return True
    # TODO: return 'error' in case of exception
    return False
