"""
Functional test of app functionality
"""

from app import app
from config import PROJECTS


#   Test data here (FIXME: move to JSON)
update_data = {
    'text': "************************************************************\nHi! You have an update available.\n************************************************************\n\n\nYou have a new update ready for download:\n\nMoodle\nMoodleWindowsInstaller-latest.zip\nReleased on 2013-04-19\n\nDownload the latest version: \n\nhttp://sourceforge.net/projects/moodle/files/latest/download?utm_campaign=updater&utm_medium=email&utm_source=subscribers\n\n************************************************************\n\nThis e-mail was intended for: bregenspan@gmail.com\n\nUnsubscribe from receiving these notifications:\nhttp://sourceforge.net/projects/moodle/unsubscribe?email=bregenspan@gmail.com\n\nManage your subscriptions:\nhttp://sourceforge.net/user/updates?email_hash=b321fa4e7c94a736c1805dabbd943f53\n\nPrivacy policy:\nhttp://slashdotmedia.com/privacy-statement/\n\n"
}
update_data['subject'] = 'Update Available: %s' % PROJECTS[0]['name']


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
