<h2 align="center">keyosk</h2>

<p align="center">
<a href="https://jwt.io/"><img alt="jwt compatible" src="https://jwt.io/img/badge-compatible.svg"></a>
<a href="https://black.readthedocs.io/en/stable/"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

Keyosk is a RESTful web service that can be used to issue application-agnostic
[JSON Web Tokens](https://jwt.io/introduction/) (JWTs).

In a [microservice based architecture](https://xkcd.com/1988/), each service only
communicates with the other services using the publicly exposed API. This promotes
more consistent and stable APIs as well as more intentionally specialized services.
However, when it comes to authentication this can present a problem: to ensure secure
authentication for a microservice-based application there are only two real options:
  * Each service must re-implement an authentication system, leading to duplicated code,
    nonstandard interfaces, and the potential for synchronization problems
  * The services must have access to a shared resource outside of their publicly
    defined APIs, which is kind of against the whole idea of microservice architectures

**Keyosk provides a third option:**

Users can authenticate against Keyosk and be issued a JSON Web Token, which can then
be used to authenticate against other microservices in the application. When a
microservice receives a user-submitted JWT it can verify with the Keyosk server that
the token a) is valid and b) hasn't been tampered with.

The workflow looks something like this:

1. User wants to submit a request to the *ToDo Service*
2. User submits username and password/API key using
   [HTTP basic auth](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication)
   to Keyosk
3. Keyosk validates the user's credentials and issues a JWT that encodes the users
   permissions, then signs the JWT using its private-key.
4. The user takes the JWT issued by Keyosk and submits their request to the
   *ToDo Service*
5. The *ToDo Service* queries Keyosk for its public-key and uses the public-key to
   verify that the JWT it just received was in fact issued by Keyosk and hasn't been
   tampered with.
6. The *ToDo Service* decodes the JWT and is able to read the permissions information
   for the user's account directly out of the JWT itself.

The application's accounts are stored in one location, the authentication workflow is
the same for all the application's components, and all the components communicate with
each other over their public API.

To learn more, [read the docs!](docs/)

## building

This project uses [Poetry](https://poetry.eustace.io/) for its build and development
system. Please [install Poetry](https://poetry.eustace.io/docs/#installation) and run
`poetry install` to create and populate the virtual environment.

```bash
# build python wheel and source distributions
make build

# build sphinx documentation in HTML format
make docs

# build sphinx documentation in another format
make docs SPHINX_FORMAT=<some other sphinx format>
```

## developing

This project requires [Poetry](https://python-poetry.org/docs/#installation) version
1.0 or newer.

```bash
# create virtual environment from lockfile
poetry install

# install pre-commit hooks
poetry run pre-commit install

# run the automated tests
poetry run tox
```
