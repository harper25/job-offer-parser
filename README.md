# JOB-OFFER-PARSER

Save and parse singular job offers posted on job portals, e.g. JustJoinIT.

## Description

The purpose of Job Offer Parser is to:

- save raw HTML content of a webpage containing job offer
- parse HTML to extract job details

It is to document currently available job offers and employees in order to get back to it for reference regarding projects and technologies when planning to change jobs. Sometimes, if a similar offer is not available and other offers are not interesting, it is ok to wait until the dream job offer appers again.

Currently supported:

- [https://justjoin.it/](https://justjoin.it/)

## Getting Started & Installing

The project was developed with [Poetry](https://python-poetry.org/docs/). Therefore you have to:

- install Poetry: [GitHub](https://github.com/sdispater/poetry)
- clone the repository
- create a virtual environment for development (ex. `poetry shell` or `virtualenv .venv`) and activate it
- cd to main folder and run: `poetry install` to install all dependencies from `pyproject.toml` in your virtual environment
- run `python -m job_offer_parser` or simply: `jobparse` with URL or file source

## Usage

```sh
usage: jobparse [-h] source

IT Job Offers Parser:
-> Download raw html of a given web page
-> Extract job offer data
-> Save the output for future reference ;)

positional arguments:
  source      Provide URL or filename with raw HTML content

options:
  -h, --help  show this help message and exit
```

## License

MIT License

## Contributing

Please, create pull requests in order to contribute.

### Taskfile

List possible linting commands with [Taskfile](https://taskfile.dev/#/):

```sh
task
```

## Authors

- [harper25](https://github.com/harper25)
