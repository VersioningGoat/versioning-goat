import glob
import requests


def write_std_readme(repo_url):
    etag = requests.head(repo_url, headers={"content-type": "text"}).headers['etag']
    sync_method = ''
    # Check if sourceforge is source
    if repo_url[7:18] == 'sourceforge':
        sync_method = 'push'
    header = "<hr>\n<img src='http://localhost:5000/status?repo_url=%s&etag=%s&sync_method=%s'> *this repository is automatically kept up to date by [the versioning goat](https://github.com/versioninggoat/versioning-goat).\n\nIt is officially maintained [here](%s).\n<hr>\n" % (repo_url, etag, sync_method, repo_url)
    # Either inject header or create full-blown readMe file.
    # TODO: add path to search for
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

# if __name__ == "__main__":
#     from sys import argv
#     write_std_readme(argv[1], argv[2], argv[3])
