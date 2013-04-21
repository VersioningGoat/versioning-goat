import string


def write_std_readme(sync_method, repo_url, etag):
    # Check if repo has readMe already
    header_template = string.Template("<hr>\n<img src='http://localhost:5000/status?repo_url=%repo_url&etag=%etag&sync_method=%sync_method'> *this repository is automatically kept up to date by [the versioning goat](https://github.com/versioninggoat/versioning-goat).\nIt is officially maintained [here](#).\n<hr>\n")
    header = header_template.substitue(repo_url=repo_url, etag=etag, sync_method=sync_method)
    filename = ''  # TODO - Find readMe
    data = ''
    if filename:
        with file(filename, 'r') as original:
            data = original.read()
    with file(filename, 'w') as modified:
            modified.write(header + data)
    # Either inject header or create full-blown readMe file.
