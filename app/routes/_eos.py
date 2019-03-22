from flask import Blueprint, render_template, abort, request
import numpy as np
import json

eos_routes = Blueprint('eos', __name__, template_folder='templates')


@eos_routes.route('/eos')
def eos():
    return render_template('eos/eos.html')


@eos_routes.route('/eos/t-s', methods=['GET', 'POST'])
def ts():

    if request.method == 'POST':
        print(request.form.get('material'))
    return render_template('eos/ts.html', data=data)

@eos_routes.route('/eos/data')
def data():
    d = [{'x': x/10, 'y': np.sin(x/10)} for x in range(100)]
    return json.dumps(d)
