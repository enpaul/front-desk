import contextlib

import _pytest
import pytest

from keyosk import config
from keyosk import database


@contextlib.contextmanager
def sqlite_database(tmp_path):
    """Database context manager for use with other fixtures that add data"""

    sqlite_path = tmp_path / "test.db"

    conf = config.ConfigSerializer().load(
        {"storage": {"backend": "sqlite", "sqlite": {"path": str(sqlite_path)}}}
    )

    database.initialize(conf)
    yield
    with contextlib.suppress(FileNotFoundError):
        sqlite_path.unlink()


@pytest.fixture(scope="module")
def demo_database(request, tmp_path_factory):
    """Generate a database with test data in it for tests"""
    # The built in tmp_path fixture is function scope so even though we want the ``demo_database``
    # fixture to be module scope it would end up behaving as if it were function scope because the
    # database file path would change for every invocation. Thus this fixture simply rebuilds the
    # tmp_path fixture internally. Relevant source code:
    # https://github.com/pytest-dev/pytest/blob/master/src/_pytest/tmpdir.py#L169
    # pylint: disable=protected-access
    tmp_path = _pytest.tmpdir._mk_tmp(request, tmp_path_factory)

    with sqlite_database(tmp_path):
        yield
