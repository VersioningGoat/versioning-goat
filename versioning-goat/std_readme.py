import glob


def write_std_readme(sync_method, repo_url, etag):
    # Check if repo has readMe already
    header = "<hr>\n<img src='http://localhost:5000/status?repo_url=%s&etag=%s&sync_method=%s'> *this repository is automatically kept up to date by [the versioning goat](https://github.com/versioninggoat/versioning-goat).\n\nIt is officially maintained [here](#).\n<hr>\n" % (repo_url, etag, sync_method)
    if len(glob.glob('README*')) > 0:
        filename = glob.glob('README*')[0]
    else:
        filename = 'README.md'
    data = ''
    try:
        original = open(filename, 'r')
        data = original.read()
        if data.startswith(header):
            data = data[len(header):]
    except IOError:
        print 'README not found'
    modified = open(filename, 'w')
    modified.write(header + data)
    # Either inject header or create full-blown readMe file.

# if __name__ == "__main__":
#     from sys import argv
#     write_std_readme(argv[1], argv[2], argv[3])
