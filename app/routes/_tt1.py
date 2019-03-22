from flask import Blueprint, render_template, abort, request, Response
import numpy as np
import json
from tt.appendices.A1 import SaturatedWater

tt1_routes = Blueprint('tt1', __name__, template_folder='templates')


@tt1_routes.route('/tt1')
def tt1():
    return render_template('tt1/tt1.html')


@tt1_routes.route('/tt1/saturated_water')
def saturated_water():
    key = request.args.get('property', default=None, type=str)
    value = request.args.get('value', default=None, type=float)
    if value is None:
        value = request.args.get('value', default=None, type=str)
        try:
            value = [float(v) for v in json.loads(value)]
        except Exception as e:
            msg = f'value must be a number or an array of numbers -> {value}'
            abort(500, msg)





    try:
        properties = SaturatedWater.get_state(key, value)
        return json.dumps(properties, ensure_ascii=False)
    except Exception as e:
        if key not in SaturatedWater.properties:
            prop_unit = [f'{p} in {u}' for p, u in SaturatedWater._prop_unit.items()]
            return f'property must be as string from {prop_unit}'
        elif value is None:

            return f'value must be a number or array of numbers'
        return f'no valid inputs -> {e}'

