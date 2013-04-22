![The Versioning Goat consumes boring static archives and excretes Git repositories.](https://raw.github.com/VersioningGoat/versioning-goat/master/logo.png)


The Versioning Goat
====================

This project seeks to address the NASA Space Apps challenge described here:
http://spaceappschallenge.org/challenge/syncing-nasa-open-source-projects/

Given a configuration listing the projects to sync (currently the only supported
source to sync from is Sourceforge), The Versioning Goat retrieves the latest
source archives for the projects, creates a Github repo for each if needed, and then
checks them in to Git.

After a project is changed on Sourceforge, imports happen at near-realtime thanks to
Sourceforge email updates.  A dedicated email address is set to receive updates for
each project, and using Sendgrid the app is called whenever a change has occurred.


Setup
------

 * Choose a hostname for the project to live at, e.g. www.nasacodesync.org
 * If needed, create a SendGrid account
 * Visit http://sendgrid.com/developer/reply, specify the hostname you would like
      to receive emails at (e.g. watch.nasacodesync.org), and the URL of The Versioning
      Goat's "ping" handler. (e.g. http://www.nasacodesync.org/ping)
 * Set up MX records on the hostname you specified earlier, following the instructions at:
     http://sendgrid.com/docs/API_Reference/Webhooks/parse.html
 * copy credentials.example.py to credentials.py and fill out your GitHub credentials
 * `pip install -r requirements.txt`



Maintenance
------------

 * Ensure the list of projects to import in config.py is up-to-date


Usage
------

 * Make sure the user account you're running under has an SSH key generated and
      added to your Github account (https://help.github.com/articles/generating-ssh-keys)
 * start server: `gunicorn -w 4 -b 127.0.0.1:8000 versioning-goat.app:app` -- (to listen for changes and sync on-change)
 * (TODO) `python app.py --sync-all` -- perform a one-time sync of all projects


Todos
------

 * Allow importing from other static file sources besides Sourceforge (this
    requires running imports on a schedule/cron)
 * Allow importing from other versioning systems, like SVN
  * Including Sourceforge SVN and Git, if many projects use them - seems like not.
 * Command for one-time sync of all projects
 * Evaluate if there's potential for merging with the other Space Apps Challenge projects that addressed this task
 * OO refactor to clearly reflect the separate import engines:
  * Static files
  * Sourceforge static files
  * SVN
  * Git

Thanks
-------

 * To NASA for space and @sarahfathallah for taking time away from another Hackathon
    project to pull together the quick logo (which depicts a goat eating archives
    and excreting rainbows e.g. Git repos)
