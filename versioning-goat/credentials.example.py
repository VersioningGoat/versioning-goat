# GitHub app credentials, obtain by registering an app at:
#   https://github.com/settings/applications/
GITHUB_ID = ''
GITHUB_SECRET = ''

# User access token, obtain by following the steps described at:
#   https://github.com/michaelliao/githubpy#authentication
#
# Specify scope='user,repo' when instantiating GitHub()
GITHUB_TOKEN = ''

GITHUB_ORGANIZATION = "VersioningGoat"

#  To enable error mails, set list of admin emails and SMTP
#    server info here
MAIL = {
    'mailto': ['ludwig@example.com'],
    'smtp_host': ('127.0.0.1', '587',),
    'smtp_user': '',
    'smtp_password': ''
}
