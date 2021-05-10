import hashlib
import requests
from app import app, db
from app.models import Payment
from app.forms import PaymentForm
from datetime import datetime
from flask import render_template, redirect, request, make_response
from config import Config
url = {'rub': 'https://core.piastrix.com/invoice/create', 'usd': 'https://core.piastrix.com/bill/create'}


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = PaymentForm()
    if request.method == 'POST':
        payment = Payment()
        summ = request.form.get('summ')
        if summ:
            summ = summ.replace(',', '.')
            try:
                summ = float(summ)
                payment.summ = summ
            except ValueError:
                return make_response(render_template(template_name_or_list='index.html'))
        else:
            return make_response(render_template(template_name_or_list='index.html'))
        description = request.form.get('description')
        if description:
            payment.description = description
        else:
            return make_response(render_template(template_name_or_list='index.html'))

        currency = request.form.get('currency')
        print(currency)
        if currency:
            payment.currency = currency
            send_time = datetime.utcnow()
            payment.send_time = send_time
            db.session.add(payment)
            db.session.commit()
        if currency == "eur":
            return make_response(redirect('/eur_form?payment_id={0}'.format(payment.id)))
        elif currency == "usd":
            res = payment_method(payment, url[payment.currency])
            return make_response(redirect(res))
        elif currency == "rub":
            return make_response(redirect('/rub_form?payment_id={0}'.format(payment.id)))
        return make_response(render_template(template_name_or_list='index.html', form=form))
    return make_response(render_template(template_name_or_list='index.html', form=form))


@app.route('/eur_form', methods=['GET', 'POST'])
def pay_form_method():
    payment_id = request.args.get('payment_id')
    payment = Payment.query.filter_by(id=payment_id).first()
    if not payment:
        return make_response(redirect('/'))
    configur = Config()
    keys_sorted = ['amount', 'currency', 'shop_id', 'shop_order_id']
    params = {
        'amount': payment.summ,
        'currency': configur.currency[payment.currency],
        'shop_id': configur.SHOP_ID,
        'shop_order_id': payment.id
    }
    sign = make_sign(keys_sorted, params)
    return make_response(render_template('eur_form.html', sign=sign, payment=payment, shop_id=configur.SHOP_ID))


@app.route('/rub_form', methods=['GET', 'POST'])
def invoice_form_method():
    payment_id = request.args.get('payment_id')
    payment = Payment.query.filter_by(id=payment_id).first()
    if not payment:
        return make_response(redirect('/'))

    response = payment_method(payment, url[payment.currency])
    data = response.get('data').get('data')
    method = response.get('data').get('method')
    action = response.get('data').get('url')

    return make_response(render_template('rub_form.html', data=data, method=method, action=action))


def payment_method(payment, url):
    config = Config()
    if payment.currency == 'rub':
        keys_sorted = ['amount', 'currency', 'payway', 'shop_id', 'shop_order_id']
        params = {
            'amount': payment.summ,
            'currency': config.currency[payment.currency],
            'payway': 'advcash_rub',
            'shop_id': config.SHOP_ID,
            'shop_order_id': payment.id
                }
        sign = make_sign(keys_sorted, params)
        params['sign'] = sign
        params['description'] = payment.description
        response = requests.post(url=url, json=params)
    else:
        keys_sorted = ['payer_currency', 'shop_amount', 'shop_currency', 'shop_id', 'shop_order_id']
        params = {
            'payer_currency': float(config.currency[payment.currency]),
            'shop_amount': str(payment.summ),
            'shop_currency': float(config.currency[payment.currency]),
            'shop_id': str(config.SHOP_ID),
            'shop_order_id': payment.id
                }
        sign = make_sign(keys_sorted, params)
        params['sign'] = sign
        params['description'] = payment.description
        response = requests.post(url=url, json=params)
        try:
            res = response.json().get('data').get('url')
        except Exception:
            res = None

        return res

    return response.json()


def make_sign(keys_sorted, params):
    config = Config()
    hash_str = str()
    for key in keys_sorted:
        hash_str = hash_str + str(params[key]) + ":" \
            if keys_sorted.index(key) != len(keys_sorted) - 1 else hash_str + str(params[key])
    hash_str = hash_str + config.SECRET_KEY
    sign = hashlib.sha256(hash_str.encode()).hexdigest()
    return sign
