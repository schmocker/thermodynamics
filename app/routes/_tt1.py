from flask import Blueprint, render_template, abort, request, Response
import numpy as np
import json
from tt.appendices.A1 import SaturatedWater
from tt.appendices.A3 import IdealGas
from tt.fluid_state import Fluid, Process, ThermoChart
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas


tt1_routes = Blueprint('tt1', __name__, template_folder='templates')


@tt1_routes.route('/tt1')
def tt1():
    return render_template('tt1/tt1.html')


@tt1_routes.route('/tt1/saturated_water')
def saturated_water():
    key = request.args.get('property', default=None, type=str)
    value = request.args.get('value', default=None, type=float)

    if value is None:
        try:
            value = request.args.get('value', default=None, type=str)
            value = [float(v) for v in json.loads(value)]
        except Exception as e:
            msg = f'value must be a number or an array of numbers -> given value: {value}'
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

@tt1_routes.route('/fluid_state')
def fluid_state():
    return render_template('tt1/fluid_state.html')

@tt1_routes.route('/fluid_state_img')
def fluid_state_img():
    props = {'p': 100, 'v': 0.02}
    f1 = Fluid(fluid_name='Water', amount=1, properties=props)
    p12 = Process(f1, 'p', 'T', 400)

    f2 = p12.state_2
    p23 = Process(f2, 'T', 'p', 230)
    f3 = p23.state_2
    p34 = Process(f3, 'p', 'v', 0.002)
    f4 = p34.state_2
    p45 = Process(f4, 'T', 'v', 1)
    f5 = p45.state_2

    chrt = ThermoChart('pv', fluid=f1.fluid_name, x_property='h', x_unit='kJ/kg', y_property='p', y_unit='bar',
                       states=[f1, f2, f3, f4, f5], processes=[p12, p23, p34, p45], x_log=False, y_log=False)

    fig = chrt.create_empty()

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@tt1_routes.route('/tt1/ideal_gas')
def ideal_gas():
    key = request.args.get('property', default=None, type=str)
    value = request.args.get('value', default=None, type=float)

    if value is None:
        try:
            value = request.args.get('value', default=None, type=str)
            value = [float(v) for v in json.loads(value)]
        except Exception as e:
            msg = f'value must be a number or an array of numbers -> given value: {value}'
            abort(500, msg)

    try:
        properties = IdealGas.get_state(key, value)
        return json.dumps(properties, ensure_ascii=False)
    except Exception as e:
        if key not in IdealGas.properties:
            prop_unit = [f'{p} in {u}' for p, u in IdealGas._prop_unit.items()]
            return f'property must be as string from {prop_unit}'
        elif value is None:

            return f'value must be a number or array of numbers'
        return f'no valid inputs -> {e}'

