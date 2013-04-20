from flask import send_file
from random import choice


def get_image(request):
    # TODO: Use actual hook instead of check_repo
    if check_repo(request.args.get('repo')):
        filename = '../assets/images/ok.png'
    else:
        filename = '../assets/images/not_ok.png'
        # TODO: Trigger Goat Worker
    return send_file(filename, mimetype='image/png')


# Mocked response
def check_repo(repo):
    if repo == "true":
        return True
    elif repo == "false":
        return False
    return choice([True, False])
