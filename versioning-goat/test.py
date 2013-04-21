"""
Functional test of app functionality
"""

from app import app
from config import PROJECTS


# Simulated data of Sourceforge email update received via Sendgrid inbound parse
update_data = dict(subject='Update Available: %s' % PROJECTS[0]['name'])


class Test(object):
    def __init__(self):
        self.client = app.test_client()

    def receive_update_notification(self):
        return self.client.post('/ping', data=update_data)


if __name__ == "__main__":
    app.testing = True
    test = Test()

    from app import setup_repos
    setup_repos()

    print(test.receive_update_notification())
