from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, TextAreaField, SelectField, FloatField
from wtforms.validators import ValidationError, DataRequired, Length


class PaymentForm(FlaskForm):
    summ = StringField("Summ", validators=[DataRequired()])
    description = TextAreaField("About good", validators=[Length(min=0, max=140)])
    currency = SelectField('Currency', choices=[('eur', 'EUR'), ('usd', 'USD'), ('rub', 'RUB')])
    submit = SubmitField('PAY')


class EURForm(FlaskForm):
    summ = FloatField("Summ")
    currency = StringField("Currency")
    shop_id = FloatField("Shop id")
    sign = StringField("Sign")
    shop_order_id = FloatField("Shop order id")
    description = StringField("Description")
    submit = SubmitField("Accept")