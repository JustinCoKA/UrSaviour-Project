import os
import importlib.util


def load_etl_module():
    here = os.path.dirname(__file__)
    module_path = os.path.abspath(os.path.join(here, '..', 'etl_processor_lambda.py'))
    spec = importlib.util.spec_from_file_location("etl_processor", module_path)
    etl = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(etl)
    return etl


def test_map_csv_fields_basic():
    etl = load_etl_module()

    csv_row = {
        'product_id': 'P0040',
        'product_name': 'Donut',
        'category_name': 'Fruit',
        'description': 'Standard pack of donut',
        'store_name': 'Justin Groceries',
        'base_price': '5.87',
        'default_image_url': '/images/p/P0040.jpg',
        'discount_type': 'Half Price',
        'final_price': '2.94'
    }

    mapped = etl.map_csv_fields(csv_row)

    assert mapped['productName'] == 'Donut'
    assert mapped['categoryName'] == 'Fruit'
    assert mapped['storeName'] == 'Justin Groceries'
    assert abs(mapped['basePrice'] - 5.87) < 0.001
    assert abs(mapped['price'] - 2.94) < 0.001
    assert mapped['offerDetails'] == 'Half Price'


def test_has_successful_job_true_and_false(monkeypatch):
    etl = load_etl_module()

    class FakeCursor:
        def __init__(self, rows):
            self._rows = rows
        def execute(self, sql, params=None):
            self._sql = sql
            self._params = params
        def fetchone(self):
            return self._rows[0] if self._rows else None
        def fetchall(self):
            return self._rows

    class FakeConn:
        def __init__(self, rows):
            self._rows = rows
        def cursor(self):
            return FakeCursor(self._rows)
        def close(self):
            pass

    # Case: existing successful job
    monkeypatch.setattr(etl, 'get_db_connection', lambda: FakeConn([{'cnt': 1}]))
    assert etl.has_successful_job('data/foo.csv') is True

    # Case: no successful job
    monkeypatch.setattr(etl, 'get_db_connection', lambda: FakeConn([{'cnt': 0}]))
    assert etl.has_successful_job('data/bar.csv') is False
