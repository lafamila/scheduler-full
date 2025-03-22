from flask import Blueprint, jsonify, request
from .connector import Connector
from datetime import datetime, timezone, timedelta
import calendar
from dateutil import relativedelta
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
        query = f"""SELECT task_id, task_title, DATE_FORMAT(target_date, '%%Y-%%m-%%d') AS target_date, task_status, parent_task_id FROM tasks 
                    WHERE user_index=1 
                    {subquery} 
                    {order}"""
        curs.execute(query, params)
        result = curs.fetchall()
    return jsonify(result)

@bp.route('/schedule', methods=['POST'])
def post_schedule():
    params = request.form.to_dict()
    if "parent_task_id" not in params:
        params["parent_task_id"] = None
    with Connector() as conn:
        curs = conn.cursor()
        curs.execute("INSERT INTO tasks(user_index, task_title, target_date, parent_task_id) VALUES (1, %(task_title)s, %(target_date)s, %(parent_task_id)s)", params)
    return jsonify({})

@bp.route('/schedule/every/<period>', methods=['POST'])
def copy_schedule(period):
    params = request.form.to_dict()
    with Connector() as conn:
        curs = conn.cursor()
        curs.execute("SELECT user_index, task_title, DATE_FORMAT(target_date, '%%Y-%%m-%%d') AS target_date, parent_task_id FROM tasks WHERE task_id=%(task_id)s", params)
        task = curs.fetchone()
        if task["parent_task_id"] is None:
            task["parent_task_id"] = params["task_id"]

        task_params = []
        if period == "week":
            for i in range(52):
                target_date = datetime.strptime(task["target_date"], "%Y-%m-%d")
                task["target_date"] = (target_date + timedelta(days=7)).strftime("%Y-%m-%d")
                task_params.append({k: v for k, v in task.items()})

        if period == "month":
            target_date = datetime.strptime(task["target_date"], "%Y-%m-%d")
            for i in range(1, 121):
                raw = {k: v for k, v in task.items()}
                raw["target_date"] = target_date + relativedelta.relativedelta(months=i)
                task_params.append(raw)

        if period == "year":
            target_date = datetime.strptime(task["target_date"], "%Y-%m-%d")
            for i in range(1, 31):
                raw = {k: v for k, v in task.items()}
                next_date = target_date + relativedelta.relativedelta(years=i)
                raw["target_date"] = next_date
                task_params.append(raw)

        curs.executemany("""INSERT INTO tasks(user_index, task_title, target_date, parent_task_id) 
                            SELECT 1, %(task_title)s, %(target_date)s, %(parent_task_id)s FROM DUAL 
                            WHERE NOT EXISTS (SELECT * FROM tasks 
                            WHERE task_title=%(task_title)s AND target_date=%(target_date)s AND parent_task_id=%(parent_task_id)s LIMIT 1)""", task_params)
        curs.execute("UPDATE tasks SET parent_task_id=%s WHERE task_id=%s", (task["parent_task_id"], params["task_id"]))

    return jsonify({})

@bp.route('/schedule/<index>', methods=['PATCH'])
def update_schedule(index):
    with Connector() as conn:
        curs = conn.cursor()
        curs.execute("UPDATE tasks SET task_status=1, mdf_dtm=%s WHERE task_id=%s", (datetime.now(tz=KST).strftime("%Y-%m-%d %H:%M:%S"), index))
    return jsonify({})
    # return jsonify(result)


@bp.route('/schedule/<index>/<parent_index>', methods=['DELETE'])
def delete_schedule(index, parent_index):
    with Connector() as conn:
        curs = conn.cursor()
        if int(parent_index) != 0:
            curs.execute("SELECT target_date FROM tasks WHERE task_id=%s", (index, ))
            task = curs.fetchone()
            curs.execute("DELETE FROM tasks WHERE parent_task_id=%s AND target_date >= %s", (parent_index, task['target_date']))
        else:
            curs.execute("DELETE FROM tasks WHERE task_id=%s", (index, ))

    return jsonify({})
    # return jsonify(result)

