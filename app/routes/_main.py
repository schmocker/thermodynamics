from flask import Blueprint, render_template

main_routes = Blueprint('main', __name__, template_folder='templates')


@main_routes.route('/')
def home():
    return render_template('main/home.html')
