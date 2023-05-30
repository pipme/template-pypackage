# Tutorial

??? Note
Did you find this article confusing? [Edit this file] and pull a request!

To start with, you will need [GitHub], [PyPI], [TestPyPI] and [Codecov] account. If
you don't have one, please follow the links to apply one before you get started on this
tutorial.

If you are new to Git and GitHub, you should probably spend a few minutes on
some tutorials at the top of the page at [GitHub Help].

## Step 1: Install Cookiecutter

Install cookiecutter:

```bash
pip install cookiecutter
```

## Step 2: Generate Your Package

Now it's time to generate your Python package.

Run the following command and feed with answers, If you don’t know what to enter, stick with the defaults:

```bash
cookiecutter https://github.com/waynerv/cookiecutter-pypackage.git
```

Finally, a new folder will be created under current folder, the name is the answer you
provided to `project_name_slug`.

Go to this generated folder, the project layout should look like:

```
python_project
├── CHANGELOG.md
├── LICENSE
├── README.md
├── docs
│   ├── api.md
│   ├── changelog.md
│   ├── index.md
│   ├── installation.md
│   └── usage.md
├── environment.yml
├── mkdocs.yml
├── mypy.ini
├── pyproject.toml
├── pytest.ini
├── python_project
│   ├── __init__.py
│   ├── __main__.py
│   └── cli.py
├── setup.py
├── tests
│   ├── __init__.py
│   ├── __pycache__
│   │   └── __init__.cpython-39.pyc
│   └── test_python_project.py
└── tox.ini
```

Here the `project_name_slug` is `python_project`, when you generate yours, it could be other name.

Also be noticed that there's `pyproject.toml` in this folder. This is the main configuration file of our project.

## Step 3: Install Dev Requirements

You should still be in the folder named as `project_name_slug`, which containing the
`pyproject.toml` file.

Install the new project's local development requirements:

```bash
conda env create -f environment.yml
```

??? Tips

    Extra dependencies are grouped into three groups, doc, dev and test for better
    granularity. When you ship the package, dependencies in group doc, dev and test
    might not be shipped.

    As the developer, you will need install all the dependencies.

??? Tips

    if you found erros like the following during tox run:
    ```
    ERROR: InterpreterNotFound: python3.9
    ```
    don't be panic, this is just because python3.x is not found on your machine. If you
    decide to support that version of Python in your package, please install it on your
    machine. Otherwise, remove it from tox.ini and pyproject.toml (search python3.x then
    remove it).

## Step 4: Create a GitHub Repo

Go to your GitHub account and create a new repo named `my-package`, where
`my-package` matches the `project_name_slug` from your answers to running
cookiecutter.

Then go to repo > settings > secrets, click on 'New repository secret', add the following
secrets:

- TEST_PYPI_API_TOKEN, see [How to apply TestPyPI token]
- PYPI_API_TOKEN, see [How to apply pypi token]
- PERSONAL_TOKEN, see [How to apply personal token]

## Step 5: Set Up codecov integration

???+ Tips

    If you have already setup codecov integration and configured access for all your
    repositories, you can skip this step.

In your browser, visit [install codecov app], you'll be landed at this page:

![](http://images.jieyu.ai/images/202104/20210419175222.png)

Click on the green `install` button at top right, choose `all repositories` then click
on `install` button, following directions until all set.

If the repo you created is a private repo, you need to set the following additional secrets,
which is not required for public repos:

- CODECOV_TOKEN, see [Codecov GitHub Action - Usage](https://github.com/marketplace/actions/codecov?version=v1.5.2#usage)

## Step 6: Upload code to GitHub

Back to your develop environment, find the folder named after the `project_name_slug`.
Move into this folder, and then setup git to use your GitHub repo and upload the
code:

```bash
cd my-package

git add .
git commit -m "Initial commit."
git branch -M main
git remote add origin git@github.com:myusername/my-package.git
git push -u origin main
```

Where `myusername` and `my-package` are adjusted for your username and
repo name.

You'll need a ssh key to push the repo. You can [Generate] a key or
[Add] an existing one.

???+ Warning

    if you answered 'yes' to the question if install pre-commit hooks at last step,
    then you should find pre-commit be invoked when you run `git commit`, and some files
     may be modified by hooks. If so, please add these files and **commit again**.

### Check result

After pushing your code to GitHub, goto GitHub web page, navigate to your repo, then
click on actions link, you should find screen like this:

![](http://images.jieyu.ai/images/202104/20210419170304.png)

There should be some workflows running. After they finished, go to [TestPyPI], check if a
new artifact is published under the name `project_name_slug`.

## Step 7. Check documentation

Documentation will be published and available at _https://{your_github_account}.github.io/{your_repo}_ once:

1. the commit is tagged, and the tag name is started with 'v' (lower case)
2. build/testing executed by GitHub CI passed

If you'd like to see what it's look like now, you could run the following command:

```
mkdocs serve
```

This will run the builtin development server for you to preview.

## Step 8. Make official release

After done with your phased development in a feature branch, make a pull request, following
instructions at [release checklist](pypi_release_checklist.md), trigger first official release and check
result at [PyPI].

[Edit this file]: https://github.com/waynerv/cookiecutter-pypackage/blob/master/docs/tutorial.md
[Codecov]: https://codecov.io/
[PYPI]: https://pypi.org
[GitHub]: https://github.com/
[TestPyPI]: https://test.pypi.org/
[GitHub Help]: https://help.github.com/
[Generate]: https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/
[Add]: https://help.github.com/articles/adding-a-new-ssh-key-to-your-github-account/
[How to apply testpypi token]: https://test.pypi.org/manage/account/
[How to apply pypi token]: https://pypi.org/manage/account/
[How to apply personal token]: https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token
[install codecov app]: https://github.com/apps/codecov
