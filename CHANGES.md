# Changes

## 0.1.2 (2019-XX-XX)

- FEATURE: `wenv init` can be used offline. A cache for installation files was added, see #1. `wenv cache` fills the cache automatically (internet connection required), `WENV_OFFLINE=true wenv init` runs the initialization of the actual *Wine Python environment* offline. Offline functionality can be configured through the new configuration parameters `prefix`, `offline`, `cache` and `packages`.
- FEATURE: Added new configuration parameter `wineinstallprefix` allowing custom wine installation paths, see #10.
- FIX: Using `requests` instead of `urllib` for loading components. Removed `certifi` workaround.
- FIX: For user installations, `sys.prefix` is not the right place to put shared resources. `site.USER_BASE` should be used instead, see #4.
- FIX: `wenv init` would trigger Wine's "update prefix" message window even when used in scripts. Now suppressed, see #5.
- FIX: `wenv pip` does not warn anymore that exe-files are not in PATH, see #6.

## 0.1.1 (2019-12-09)

* FIX: `wenv` installed its environment into `shared` folder instead of `share`.
* FIX: Broken links in README.md

## 0.1.0 (2019-12-08)

`wenv` broken out of [`zugbruecke`](https://github.com/pleiszenburg/zugbruecke) and turned into an independent package. The following changes were made since `zugbruecke` 0.0.14.

| **OLD**                               | **NEW**                            |
| ------------------------------------- | ---------------------------------- |
| `wine-python`                         | `wenv python`                      |
| `wine-pip`                            | `wenv pip`                         |
| `wine-pytest`                         | `wenv pytest`                      |
| `#!/usr/bin/env wine-python`          | `#!/usr/bin/env _wenv_python`      |
| `{"version": "3.5.3"}`                | `{"pythonversion": "3.7.4"}`       |

The above significant change was mandatory for allowing to cleanup a lot of old code and to remove long-standing bugs.

The shell scripts ``wine-python``, ``wine-pip`` and ``wine-pytest`` have been removed. Their functionality was consolidated into a single new script, ``wenv``. One can now call ``wenv python``, ``wenv pip`` and ``wenv pytest``. This change was necessary for allowing a more generic interface to entry points of arbitrary third party packages. Run ``wenv help`` for more information.

The ``version`` configuration parameter for controlling the version of *Wine Python* has been renamed to ``pythonversion``.

Wine 2.x and 3.x are no longer supported. Please use Wine 4.x or later.

On older versions of Linux such as *Ubuntu 14.04* alias *Trusty Tahr* (released 2014), you may observe errors when running ``wenv python``. Most commonly, they will present themselves as ``OSError: [WinError 6] Invalid handle: 'z:\\...`` triggered by calling ``os.listdir`` on a symbolic link ("symlink") to a folder.

*wenv* will use semantic versioning. Breaking changes will be indicated by increasing the first version number, the major version. Going for example from 0.x.0 to 1.0.0 or going from 1.y.0 to 2.0.0 therefore indicates a breaking change.

* FEATURE: Allow `-h` and `--help` as alternatives to `help`.
* FEATURE: ``wineprefix``, ``winedebug`` and ``pythonprefix`` become configuration parameters definable by users allowing custom wine prefixes, wine debug levels and Python installation paths, see issue zugbruecke#44.
* FEATURE: All configuration parameters can be overridden with individual environment variables.
* FEATURE: Introduced new exception types specific to *wenv*. Meaningful exception are now raised throughout the package.
* FEATURE: Added official support for CPython 3.8, see zugbruecke#56.
* FEATURE: *Wine Python* can be based on beta versions and release candidates of *CPython*.
* FIX: ``wine-pip`` previously would, on every launch, download ``get-pip.py`` and try to install it first before running - even if ``pip`` was already installed. ``wenv pip`` does not show this behavior anymore.
* FIX: ``wine-python``, ``wine-pip`` and ``wenv pytest`` implicitly depended on ``bash``. This dependency has been removed in their successor ``wenv``, see zugbruecke#48.
* FIX: ``wine-python`` would fail on systems with old versions of ``libssl`` or broken SSL certificate store configurations, see zugbruecke#51. For details on the implemented workaround, see installation instructions in the documentation.
* The configuration module was refactored and made clearer and faster, allowing to implement new options.
