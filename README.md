# SeleniumProbes

 ![Python 3.6+](https://img.shields.io/badge/Python-3.6+-blue.svg) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)][BlackRef] [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)][MITRef]

[BlackRef]: https://github.com/ambv/black
[MITRef]: https://opensource.org/licenses/MIT

`SeleniumProbes` is a library of building blocks to construct probes generating metrics for automated testing of web app performance and availability like accessing a login page, authenticating on it and then triggering some functionality by clicking on a web element.

## Getting Started

Follow these instructions to use the package in your project.

### Installing

`SeleniumProbes` library could be added to your project by installing it from the Python Package Index (PyPI) repository. Run the following command to:

* install a specific version

    ```sh
    pip install "selenium_probes==0.1"
    ```

* install the latest version

    ```sh
    pip install "selenium_probes"
    ```

* upgrade to the latest version

    ```sh
    pip install --upgrade "selenium_probes"
    ```

* install optional dependencies like Microsoft Azure libraries to use KeyVault helper to work (not everybody would need that, hence it is an optional dependency)

    ```sh
    pip install "selenium_probes[keyvault]"
    ```

### Requirements

PyPI packages:

* Python >= 3.6
* [selenium >= 3.141.0][SeWebDriverRef]


[SeWebDriverRef]: https://pypi.org/project/selenium/

### Deployment

This library package is not intended for stand-alone deployment. It should be used as part of some webapp-specific probe. See [SeleniumBottle][SeleniumBottleProjectRef] project as an example.

[SeleniumBottleProjectRef]: https://github.com/undp/SeleniumBottle

## Built using

* [Selenium WebDriver][SeWebDriverRef] - Web browser interactions

## Versioning

We use [Semantic Versioning Specification][SemVer] as a version numbering convention.

[SemVer]: http://semver.org/

## Release History

For the available versions, see the [tags on this repository][RepoTags]. Specific changes for each version are documented in [CHANGES.md][ChangelogRef].

Also, conventions for `git commit` messages are documented in [CONTRIBUTING.md][ContribRef].

[RepoTags]: https://github.com/undp/SeleniumProbes/tags
[ChangelogRef]: CHANGES.md
[ContribRef]: CONTRIBUTING.md

## Authors

* **Oleksiy Kuzmenko** - [OK-UNDP@GitHub][OK-UNDP@GitHub] - *Initial work*

[OK-UNDP@GitHub]: https://github.com/OK-UNDP

## Acknowledgments

* Hat tip to anyone helping.

## License

Unless otherwise stated, all authors (see commit logs) release their work under the [MIT License][MITRef]. See [LICENSE.md][LicenseRef] for details.

[LicenseRef]: LICENSE.md

## Contributing

There are plenty of ways you could contribute to this project. Feel free to:

* submit bug reports and feature requests
* outline, fix and expand documentation
* peer-review bug reports and pull requests
* implement new features or fix bugs

See [CONTRIBUTING.md][ContribRef] for details on code formatting, linting and testing frameworks used by this project.
