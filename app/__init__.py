"""Flask app factory."""
from typing import List

from flask import Flask
from flask import request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, text
from sqlalchemy.orm import join

db = SQLAlchemy()


def create_app(config_class: object):
    """Create Flask app.

    Args:
        config_class: configuation for Flask app
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    @app.route("/ping", methods=["GET", "POST"])
    def ping() -> str:
        """Return string to show the server is alive."""
        return "Server is here"

    @app.route("/metrics", methods=["GET"])
    def metrics() -> List:
        from flask import jsonify
        from sqlalchemy.orm import aliased
        from app.models import Metric

        requested_metric_value = int(request.args.get('metric_value'))

        metric1 = Metric.__table__
        metric2 = aliased(Metric.__table__)

        query = join(metric1, metric2, metric1.c.artist_id == metric2.c.artist_id).select().where(
            and_(metric1.c.value >= requested_metric_value, metric2.c.value < requested_metric_value,
                 metric2.c.date == metric1.c.date - text('INTERVAL 24 HOURS')))

        queryset_data = db.session.connection().execute(query).fetchall()

        return jsonify(queryset_data)

    return app
