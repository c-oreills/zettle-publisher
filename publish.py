from datetime import datetime
import os
import re

import git


zettle_path = os.environ.get("ZETTLE_PATH")
repo_path = os.environ.get("REPO_PATH")
pages_subpath = os.environ.get("PAGES_SUBPATH", "z")
publish_tag = os.environ.get("OPEN_TAG", "#PublishToPages")

publish_re = re.compile(publish_tag + r"\s*\(([\w-]+)\)")

assert publish_re.match(publish_tag + "(test-url)")


def copy_files_to_pages():
    for file_name in os.listdir(zettle_path):
        full_path = os.path.join(zettle_path, file_name)

        # Check if the file is a regular file (not a directory)
        if not os.path.isfile(full_path):
            continue

        # Just handle Markdown for now
        if not full_path.endswith('.md'):
            continue

        with open(full_path) as f:
            if publish_match := publish_re.search(f.read()):
                publish_url = publish_match.group(1)
                copy_file_to_pages(file_name, f, publish_url)


PAGE_FRONTMATTER = """---
layout: page
title: {title}
exclude: true
---
"""


def copy_file_to_pages(file_name, src_f, publish_url):
    title = file_name[:-3]
    print(f"Writing {publish_url}, title {title}")
    repo_full_path = os.path.join(repo_path, pages_subpath, publish_url + '.md')
    with open(repo_full_path, 'w') as dst_f:
        # Return to start of src file
        src_f.seek(0)
        dst_f.write(PAGE_FRONTMATTER.format(title=title))
        for l in src_f.readlines():
            # Omit the open tag line
            if publish_tag in l:
                continue

            dst_f.writelines((l,))


def commit():
    repo = git.Repo(repo_path)

    repo.git.add(all=True)

    commit_message = f"Updates as of {datetime.now()}"
    repo.git.commit(m=commit_message)

    repo.git.push()


copy_files_to_pages()
#commit()
