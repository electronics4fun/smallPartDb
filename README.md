# smallPartDb

[![license](https://img.shields.io/github/license/:user/:repo.svg)](LICENSE)

## Table of Contents

- [Background](#background)
- [Requirements](#requirements)
- [Install](#install)
- [Usage](#usage)
- [Limitations](#note)
- [Maintainers](#maintainers)
- [Contributing](#contributing)
- [License](#license)

## Background
Small python class for interfacing [Part-Db](https://github.com/Part-DB/Part-DB-server) based on request package.

## Requirements
* Setup a file with name "settings.yaml" with your credentials like:
```python
{
    token : "tcp_yourBearerToken",
    host : "localhost"
}
```
* Setup a user for API access in Part-Db.

## Install
See ![requirements.txt](/requirements.txt).

## Limitations
Not all functionality of Part-DB is supported yet, but the most important ones.
Settings parameter max-value and min-value seems to have a problem.

Take a look at "partDbExample.py" for usage.


## Maintainers
[@electronics4fun](https://github.com/electronics4fun)


## Contributing
Feel free to dive in! [Open an issue](https://github.com/electronics4fun/smallPartDb/issues/new) or submit PRs.


## License
[MIT](LICENSE)
