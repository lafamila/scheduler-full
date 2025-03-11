from flask import Blueprint, jsonify, request
from .connector import Connector
from datetime import datetime, timezone, timedelta
KST = timezone(timedelta(hours=9))
bp = Blueprint('api', __name__, url_prefix='/api')
@bp.before_request
def update_schedule_auto():
    params = {"today": datetime.now(tz=KST).strftime("%Y-%m-%d")}
    with Connector() as conn:
        curs = conn.cursor()
        curs.execute("UPDATE tasks SET target_date=%(today)s WHERE task_status=0 AND target_date < %(today)s", params)


@bp.route('/schedule', methods=['GET'])
def get_schedule():
    params = request.args.to_dict()
    subquery = "AND target_date=%(target_date)s" if "target_date_st" not in params else "AND target_date BETWEEN %(target_date_st)s AND %(target_date_ed)s"
    order = "ORDER BY target_date, task_status, task_id ASC" if "year" not in params else "ORDER BY YEAR(target_date), task_status, task_id ASC"
    with Connector() as conn:
        curs = conn.cursor()
        query = f"""SELECT task_id, task_title, DATE_FORMAT(target_date, '%%Y-%%m-%%d') AS target_date, task_status FROM tasks 
                    WHERE user_index=1 
                    {subquery} 
                    {order}"""
        curs.execute(query, params)
        result = curs.fetchall()
    return jsonify(result)

@bp.route('/schedule', methods=['POST'])
def post_schedule():
    params = request.form.to_dict()
    with Connector() as conn:
        curs = conn.cursor()
        curs.execute("INSERT INTO tasks(user_index, task_title, target_date) VALUES (1, %(task_title)s, %(target_date)s)", params)
    return jsonify({})

@bp.route('/schedule/<index>', methods=['PATCH'])
def update_schedule(index):
    with Connector() as conn:
        curs = conn.cursor()
        print(datetime.now(tz=KST).strftime("%Y-%m-%d %H:%M:%S"))
        curs.execute("UPDATE tasks SET task_status=1, mdf_dtm=%s WHERE task_id=%s", (datetime.now(tz=KST).strftime("%Y-%m-%d %H:%M:%S"), index))
    return jsonify({})
    # return jsonify(result)
