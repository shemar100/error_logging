from my_app import db, es, app
from flask_wtf import FlaskForm
from decimal import Decimal
from wtforms import  DecimalField, SelectField, StringField
from wtforms.validators import InputRequired, NumberRange, ValidationError
from wtforms.widgets import html_params, Select, HTMLString
from flask_wtf.file import FileField, FileRequired
from blinker import Namespace

#signal declarations have a global scope and can be implemented in any file
catalog_signals = Namespace()
product_created = catalog_signals.signal('product-created')
category_created = catalog_signals.signal('category-created')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(244))
    image_path = db.Column(db.String(255))
    price = db.Column(db.Float)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref=db.backref('products', lazy='dynamic'))

    def __init__(self, name, price, category, image_path):
        self.name = name
        self.price = price
        self.category = category
        self.image_path = image_path

    def add_product_index_to_es(sender, product):
        es.index(index='catalog', body={
            'name': product.name,
            'category': product.category.name
        }, id=product.id)
        es.indices.refresh(index='catalog')
    
    product_created.connect(add_product_index_to_es, app)
    
    def __repr__(self):
        return 'Product<%d> ' % self.id

class Category(db.Model):
    id =  db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __init__(self, name):
        self.name = name

    def add_category_index_to_es(sender, category):
        es.index(index='catalog', body={
            'name': category.name,
        }, id=category.id)
        es.indices.refresh(index='catalog')
    category_created.connect(add_category_index_to_es, app)

    def __repr__(self):
        f'<Category> {self.id}'

class CustomCategoryInput(Select):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = []
        for val, label, selected in field.iter_choices():
            html.append(
                '<input type="radio" %s> %s' % (
                    html_params(
                        name=field.name, value=val, checked=selected, **kwargs
                    ), label
                )
            )
        return HTMLString(' '.join(html))

class CategoryField(SelectField):
    def iter_choices(self):
        categories = [(c.id, c.name) for c in Category.query.all()]
        for value, label in categories:
            yield (value, label, self.coerce(value) == self.data)
    
    def pre_validate(self, form):
        for v, _ in [(c.id, c.name) for c in Category.query.all()]:
            if self.data == v:
                break
            else:
                raise ValueError(self.gettext('Not a valid choice'))

class NameForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
 
class ProductForm(NameForm):
    price = DecimalField('Price', validators=[
        InputRequired(), NumberRange(min=Decimal('0.0'))
    ])
    category = CategoryField('Category', validators=[InputRequired()], coerce=int)
    image = FileField('Product Image', validators=[FileRequired()])

def check_duplicate_category(case_sensitive=True):
    def _check_duplicate(form, field):
        if case_sensitive:
            res = Category.query.filter(
                Category.name.like('%' + field.data + '%')
            ).first()
        else:
            res = Category.query.filter(
                Category.name.like('%' + field.data + '%')
            ).first()
        if res:
            raise ValidationError('Category named {field.data} already exists')
    return _check_duplicate


class CategoryForm(NameForm):
    name = StringField('Name', validators=[InputRequired(), check_duplicate_category()])


