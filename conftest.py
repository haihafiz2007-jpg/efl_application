import pytest
import database

@pytest.fixture
def db_file(tmp_path):
    path=str(tmp_path / "test.db")
    database.init_db(path)
    return path