# Contributing

This projects follows the [Gitflow workflow][WorkflowRef]. When contributing, please discuss the change you wish to make via [Issues][IssuesRef], email, or any other method with the maintainers of this repository before raising a [Pull Request](#pull-request-process).

[WorkflowRef]: https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow
[IssuesRef]: https://github.com/undp/SeleniumProbes/issues

## Dev Environment

In order to be consistent with all required dependencies, you would need to use `poetry`. See the [Dependencies](#dependencies) section below on how to install it.

We would also recommend to have a dedicated Python virtual environment created for this project. See [this section](#managing-virtual-environments) for more info on virtual environments.

To start with the project:

```sh
git clone https://github.com/undp/seleniumprobes.git SeleniumProbes
cd SeleniumProbes
pre-commit install
poetry install
```

If you are just starting to work with Python, read the sections below for more detailed explanation on how to create an efficient Python dev environment.

### Dependencies

We build our project into a package and distribute it to PyPI with `poetry`. We also use it to manage code dependencies. You would need to have `poetry` installed with the following command:

```sh
curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
```

### Formatting

[PEP-8 Style Guide for Python Code][PEP-8] suggests a set of rules to format code in a certain way for better structure and readability. However, these stylistic recommendations could be interpreted in more than one way producing code formatting styles which are PEP8-compliant but different from one another.

[PEP-8]: https://www.python.org/dev/peps/pep-0008/

To make our development more efficient and our code more consistent, we cede control over code formatting to `black`. As explained on [black's GitHub page][BlackGitHub]:

[BlackGitHub]: https://github.com/python/black

> Black is the uncompromising Python code formatter. [...] Blackened code looks the same regardless of the project you're reading. Formatting becomes transparent after a while and you can focus on the content instead.

Code examples from Python `docstrings` (documentation embedded into the code) could be also formatted using `black` conventions with the help of `blacken-docs` tool.

Also, some IDEs like [Visual Studio Code][VSCodeGitHub] allow `black` formatting action to be performed on each file saving operation, if configured. To have `black` and `blacken-docs` tools for manual usage from the command-line or by your IDE, install them with the following command in your virtual environment:

```sh
poetry install -v --no-dev --extras=code-format
```

[VSCodeGitHub]: https://github.com/Microsoft/vscode

`black` formatter is automatically executed prior to committing changes to this repository with the help of `pre-commit` tool.

### Linting

Linting is a process of scanning the code for stylistic or syntactic problems which is different from code formatting. Linting analyses how code runs and helps to detect things like undefined variables or functions as well as some logical errors with your code.

This project relies on the `flake8` linter with the following plugins installed:

* `flake8-import-order` - checks the ordering of imports
    > Note: this project uses `cryptography` ordering style
* `flake8-bandit` - checks for common security issues with `bandit`
* `flake8-bugbear` - finds likely bugs and design problems
* `flake8-builtins` - validates that names of variables or parameters do not match Python builtins
* `flake8-docstrings` - checks [PEP 257][PEP-257] docstring conventions with `pydocstyle`
* `flake8-logging-format` - checks logging format strings
* `pep8-naming` - checks [PEP 8][PEP-8] naming conventions

[PEP-257]: https://www.python.org/dev/peps/pep-0008/

Similarly to the `black` formatting, linting with `flake8` is executed at every commit by `pre-commit` tool.

If you want to install `flake8` for manual usage or IDE integration, run the following command in your virtual environment:

```sh
poetry install -v --no-dev --extras=code-lint
```

### Testing

This project uses `pytest` framework to outline unit tests and `tox` to manage test environments and the workflow. Since our tests expect Selenium Grid infrastructure to be available, you would need to have `docker` in your dev environment as well.

This repo has the `docker-compoes.yaml` file outlining minimal Selenium Grid deployment. Test fixture `selenium_grid` from `tests/fixtures/test_browser.py` uses it to deploy the required minimal infrastructure with `Chrome` and `Firefox` nodes to use.

If you have a dedicated Selenium Grid infrastructure available as part of your DevOps CI/CD environment, you could re-define `SE_ENDPOINT` variable in `tox.ini` or in your environment (in this case, don't forget to comment it out from `tox.ini`).

Our tests rely on the following `pytest` plugins:

* `pytest-cov` - to ensure adequate test coverage
* `pytest-dockerc` - to deploy `docker-compose.yaml` into the test environment
* `pytest-instafail` - to report failures while the test run is happening
* `pytest-lazy-fixture` - to use test fixtures in `pytest.mark.parametrize` decorator
* `pytest-random-order` - to randomize the order in which tests are run
* `pytest-variables` - to provide variables to tests (used to provide credentials to test Azure KeyVault helper)

> **NOTE:** We expect 90% or more of the code in this project to be covered with tests, otherwise testing is configured to fail. We try to maintain this test coverage level and would ask you to cover features or bug fixes you introduce with enough test code.

In order to get just the packages to facilitate testing, run:

```sh
poetry install -v --extras=test
```

#### Sensitive Variables

In order to provide credentials for tests to access Azure KeyVault, place `creds_keyvault.yaml` into `instance/` folder in the project directory. The file should have the following variables defined:

```yaml
SP_APPID: {{ AppID of the Service Principle }}
SP_PWD: {{ Secret of the Service Principle }}
SP_TENANT: {{ Tenand ID of the Service Principle}}

VAULT_NAME: {{ Name of the KeyVault }}
VAULT_SECRET: {{ Name of the secret to use in tests }}
```

#### Limitations

Please note that for now all tests are executed against live targets on the Internet like:

* `http://httpbin.org`
* `http://duckduckgo.com`

Depending on your connectivity, some tests might fail (e.g. due to timeout). In the ideal situation tests should be performed against mocked fixtures to guarantee the same results everywhere. We will try to fix this in future releases.

#### Execute

To run all tests for all available versions of Python and generate HTML docs as well as test coverage reports, execute:

```sh
tox
```

If you want to execute a specific test environment mentioned in the `envlist` variable under `[tox]` section of the `tox.ini` file, run:

```sh
tox -e <env-name>
```

For example, you could just run linting with:

```sh
tox -e linting
```

Or, test Azure KeyVault helper on Python3.6 with:

```sh
tox -e py36-azure
```

### Commit messages

This project uses `gitchangelog` to automatically generate the content of [CHANGELOG.md](CHANGELOG.md). So, it is important to follow a convention on how to format your `git commit` messages. In general, all commit messages should follow the structure below:

```sh
<subject>
<BLANK LINE>
<body>
```

`<subject>` should follow the standard `gitchangelog` convention below. See  `gitchangelog.rc` [example][GitHubGitchangelog] on GitHub for more information.

[GitHubGitchangelog]: https://github.com/vaab/gitchangelog/blob/master/.gitchangelog.rc

* `ACTION: [AUDIENCE:] SUBJ_MSG [!TAG ...]`

* `ACTION` indicates **WHAT** the change is about.
  * `chg` is for refactor, small improvement, cosmetic changes, etc
  * `fix` is for bug fixes
  * `new` is for new features, big improvement

* `AUDIENCE` indicates **WHO** is concerned by the change.
  * `dev`  is for developers (API changes, refactoring...)
  * `user`  is for final users (UI changes)
  * `pkg`  is for packagers (packaging changes)
  * `test` is for testers (test only related changes)
  * `doc`  is for tech writers (doc only changes)

* `SUBJ_MSG` is the subject itself.

* `TAGs` are for commit filtering and are preceded with `!`. Commonly used tags are:
  * `refactor` is obviously for refactoring code only
  * `minor` is for a very meaningless change (a typo, adding a comment)
  * `cosmetic` is for cosmetic driven change (re-indentation, etc)
  * `wip` is for partial functionality.

* `EXAMPLES`:
  * `new: usr: support of bazaar implemented.`
  * `chg: re-indent some lines. !cosmetic`
  * `new: dev: update code to be compatible with killer lib ver1.2.3.`
  * `fix: pkg: update year of license coverage.`
  * `new: test: add tests around usability of feature Foo.`
  * `fix: typo in spelling. !minor`

### Documentation

We strive to keep our code well documented with Python [docstrings][PEP-257-docstring]. This approach streamlines documentation maintenance by keeping it in one place with the code. Our project follows [NumPy Style][NumPyDocstrings] convention for `docstrings` to make them easy to read in place.

[PEP-257-docstring]: https://www.python.org/dev/peps/pep-0257/#what-is-a-docstring
[NumPyDocstrings]: https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard

Also, we generate well-structured HTML documentation out of docstrings with `sphinx` using `ReadTheDocs` theme. Here are the packages required for that:

```sh
poetry install -v --no-dev --extras=docs
```

You could generate local version of the HTML documentation (placed in `docs/_build/`) for this project with the following command:

```sh
tox -e docs
```

For more information on how you could document your Python code, read [this awesome article][RealPythonDocs] from Real Python web site.

[RealPythonDocs]: https://realpython.com/documenting-python-code/

### Debugging

You could enable log output while running tests by editing `[pytest]` section of `tox.ini` and having `log_cli = true` there. This would allow you to have more details on how tests are executed and address possible issues.

### Managing multiple versions of Python

Most likely, your operating system comes with some version of Python pre-installed. But, sooner or later you would need to install another version of Python to ensure your code runs on that version as well or to try new features of the language.

`pyenv` is there to help you coherently manage different versions of Python. It also has an addon `pyenv-virtualenv` to manage virtual environments (see below). You could learn more about `pyenv` and how to install it in [this article][RealPythonPyenv].

[RealPythonPyenv]: https://realpython.com/intro-to-pyenv/

### Managing Virtual Environments

Most Python applications depend on code that offers more features than the standard built-in libraries. Python distributes this third-party libraries in `packages` that you could download and use in your environment.

But what if you need to test two different versions of the same package for a specific app? If you use system-wide Python packages, you could have only one version at a time. Changing system-wide packages might also break other apps you are working on. It could even affect operating system functionality if it relies on the package you overwrote with a different version.

To address this issue Python offers a concept of virtual environments, aka `virtualenv` or `venv`. As mentioned above, in addition to managing Python versions `pyenv` can manage your environments as well. Same `pyenv` article referenced above has a section [Working With Multiple Environments][RealPythonPyenvVenv] describing how you could create and use different virtual environments for your projects. You could also read more about virtual environments in general in this [article][RealPythonVenv].

[RealPythonPyenvVenv]: https://realpython.com/intro-to-pyenv/#working-with-multiple-environments
[RealPythonVenv]: https://realpython.com/python-virtual-environments-a-primer/

#### TL;DR

Follow the steps below for Ubuntu 16.04 OS in order to install `pyenv` and create a virtual environment for the project.

1. Install these build dependencies to allow `pyenv` to compile and install different versions of Python.

    ```sh
    sudo apt install -y make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
    libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl
    ```

1. Run the `pyenv-install` script.

    ```sh
    curl https://pyenv.run | bash
    ```

1. After the installation you should see a message like this (the message might differ based on your OS and command-line shell):

    ```sh
    WARNING: seems you still have not added 'pyenv' to the load path.

    # Load pyenv automatically by adding
    # the following to ~/.bashrc:

    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
    ```

    Follow the instructions from the final messsage to configure your shell to change environments automatically when you enter/leave project folders.

1. Run the following command to create a dedicated virtual environment with Python 3.6.8.

    ```sh
    pyenv virtualenv 3.6.8 selenium-probes-venv-3.6.8
    ```

1. Also, do not forget to run the following command from the inside of the project folder to make this virtual environment the default for the project.

    ```sh
    pyenv local selenium-probes-venv-3.6.8
    ```

## Pull Request Process

1. Clone the repo to your workstation:

    ```sh
    git clone https://github.com/undp/seleniumprobes.git SeleniumProbes
    ```

1. Switch to the `develop` branch:

    ```sh
    git checkout develop
    ```

1. Create a new feature branch named `feature/fooBar` from the `develop` branch:

    ```sh
    git checkout -b feature/fooBar
    ```

1. Introduce your modifications locally. Don't forget about corresponding tests!

1. Commit your changes. Ensure your commit message follows the formatting convention [described above](#commit-messages).

    ```sh
    git commit -am "new: usr: add fooBar feature. (close #123)"
    ```

1. Push the `feature/fooBar` branch to the remote origin

    ```sh
    git push origin feature/fooBar
    ```

1. Create a new Pull Request for the repo.

1. You may merge the Pull Request in once you have the sign-off from a repo owner. Or, if you do not have permission to merge, you may request the reviewer to merge it for you.
