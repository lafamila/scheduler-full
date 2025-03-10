from flask import Blueprint, jsonify

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/schedule')
def get_schedule():
    dummmies = []
    return jsonify(dummmies)