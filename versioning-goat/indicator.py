from flask import send_file
from config import PROJECTS
import app
import requests
import threading


def get_image(request):
    # FIX-ME: Should check if project has not changed repo_url before comparing eTags
    # Checks for repos with push enabled (aka SourceForge)
    repo_url = request.args.get('repo_url')
    if request.args.get('sync_method') == 'push':
        filename = '../assets/images/goat_ok.png'
        return send_file(filename, mimetype='image/png', add_etags=False)
    # Checks for goat-loving static files
    check = up_to_date(repo_url, request.args.get('etag'))
    if check is True:
        filename = '../assets/images/goat_ok.png'
    elif check is False:
        filename = '../assets/images/goat_work.png'
        for project in PROJECTS:
            if project['url'] in repo_url:
                syncing = False
                for control_thread in threading.enumerate():
                    if control_thread.name == repo_url:
                        syncing = True
                        break
                if syncing is False:
                    sync_thread = threading.Thread(group=None, target=app.sync_url_to_repo, name=repo_url, args=([project]), kwargs={})
                    sync_thread.start()
                break
    else:
        filename = '../assets/images/goat_error.png'
    return send_file(filename, mimetype='image/png', add_etags=False)


def up_to_date(repo_url, etag):
    if repo_url and etag:
        try:
            new_etag = requests.head(repo_url, headers={"content-type": "text"}).headers['etag']
            if etag == new_etag:
                return True
        except requests.RequestException:
            return 'error'
    return False
