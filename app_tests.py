import os
from my_app import app, db
import unittest
import tempfile


class CatalogTestCase(unittest.TestCase):

    def setUp(self):
        self.test_db_file = tempfile.mkstemp()[1]
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + self.test_db_file
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        os.remove(self.test_db_file)

    def test_s(self):
        "Test products list page"
        rv = self.app.get('/products')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue('No Next Page' in rv.data.decode("utf-8"))
        self.assertTrue('No Previous Page' in rv.data.decode("utf-8"))

    def test_create_category(self):
        "Test the creation of a new category"
        rv = self.app.get('/category-create')
        self.assertEqual(rv.status_code, 200)

        rv = self.app.post('/category-create')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue('This field is required.' in rv.data.decode("utf-8"))

        rv = self.app.get('/categories')
        self.assertEqual(rv.status_code, 200)
        self.assertFalse('Phones' in rv.data.decode("utf-8"))

        rv = self.app.post('/category-create', data={
            'name' : 'Phones'
        })

        self.assertEqual(rv.status_code, 302)

        rv = self.app.get('/categories')
        self.assertEqual(rv.status_code,200)
        self.assertTrue('Phones' in rv.data.decode("utf-8"))

        rv = self.app.get('/category/1')
        self.assertEqual(rv.status_code,200)
        self.assertTrue('Phones' in rv.data.decode("utf-8"))

    def test_create_product(self):
        "Test the creation of new product"
        rv = self.app.get('/product-create')
        self.assertEqual(rv.status_code,200)

        rv = self.app.post('/product-create')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue('This field is required.' in rv.data.decode("utf-8"))

        # Create catategory to be used in product model creation
        rv = self.app.post('/category-create', data={
            'name' : 'Phones'
        })

        self.assertEqual(rv.status_code, 302)

        rv = self.app.post('/product-create', data={
            'name' : 'Iphone 5',
            'price' : 549.49,
            'category' : 1,
            'image' : tempfile.NamedTemporaryFile()
        })

        self.assertEqual(rv.status_code, 302)

        rv = self.app.get('/products')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue('Iphone 5' in rv.data.decode("utf-8"))

    def test_search_product(self):
        "Test seaching product"
        # Create a category to be used in product creation
        rv  = self.app.post('/category-create', data= {
            'name' : 'Iphones'
        })

        self.assertTrue(rv.status_code, 302)

        rv  = self.app.post('/product-create', data= {
            'name' : 'Iphone 5', 
            'price' : 549.49,
            'category' : 1,
            'image' : tempfile.NamedTemporaryFile()

        })
        self.assertTrue(rv.status_code, 302)

        rv  = self.app.post('/product-create', data= {
            'name' : 'Galaxy S5', 
            'price' : 549.49,
            'category' : 1,
            'image' : tempfile.NamedTemporaryFile()

        })
        self.assertTrue(rv.status_code, 302)

        self.app.get('/')

        rv = self.app.get('/product-search?name=iPhone')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue('Iphone 5' in rv.data.decode("utf-8"))
        self.assertFalse('Galaxy S5' in rv.data.decode("utf-8"))

        rv = self.app.get('/product-search?name=iPhone 6')
        self.assertEqual(rv.status_code, 200)
        self.assertFalse('iPhone 6' in rv.data.decode("utf-8"))
        


if __name__ == '__main__':
    unittest.main()
