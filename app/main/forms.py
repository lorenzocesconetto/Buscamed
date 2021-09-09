from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SubmitField, FloatField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp, Length, Optional


class EditProductPriceForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(
        1, 256)], render_kw={'readonly': True})
    price = FloatField('Preço', validators=[Optional()])
    promotion_price = FloatField('Preço promocional', validators=[Optional()])
    promotion_qty = IntegerField(
        'Quantidade promocional', validators=[Optional()])
    submit = SubmitField('Salvar')


class SearchForm(FlaskForm):
    q = TextField('Search', id="search-med",
                  validators=[Optional(), Length(0, 128)])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
