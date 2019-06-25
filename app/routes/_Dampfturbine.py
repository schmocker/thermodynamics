from flask import Blueprint, render_template, abort, request
import numpy as np
import json

Dampfturbine_routes = Blueprint('Dampfturbine', __name__, template_folder='templates')


@Dampfturbine_routes.route('/Dampfturbine')
def main():
    return render_template('Dampfturbine/main.html')

