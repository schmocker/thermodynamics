from flask import Blueprint, render_template, abort, request
import numpy as np

tt1_routes = Blueprint('tt1', __name__, template_folder='templates')


@tt1_routes.route('/tt1')
def tt1():
    return render_template('tt1/tt1.html')


