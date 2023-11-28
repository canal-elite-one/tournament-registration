from flaskr.db import Categories, session
from testing_data import correct_category_dicts
from sqlalchemy import select


class TestCategories:
    def test_to_dict(self):
        cat = Categories(**(correct_category_dicts[0]))
        cat_dict = cat.to_dict()
        for key, item in correct_category_dicts[0].items():
            assert key in cat_dict
            assert cat_dict[key] == correct_category_dicts[0][key]

    def test_repr(self):
        cat = Categories(**(correct_category_dicts[2]))
        assert cat.__repr__() == correct_category_dicts[2].__repr__()

    def test_select_unique(self):
        result = session.scalar(select(Categories).where(Categories.category_id == "A"))
        assert result.category_id == "A"

    def test_select_multiple(self):
        result = session.scalars(select(Categories).order_by(Categories.start_time)).all()
        print(type(result), result)

