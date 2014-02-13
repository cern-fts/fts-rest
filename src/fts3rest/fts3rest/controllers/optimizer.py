from datetime import datetime, timedelta
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3.model import OptimizerEvolution
from pylons import config, request


class OptimizerController(BaseController):
    """
    Optimizer logging tables
    """

    @doc.return_type(bool)
    @jsonify
    def isEnabled(self):
        """
        Indicates if the optimizer is enabled in the server
        """
        return config['fts3.Optimizer']

    @doc.return_type(array_of=OptimizerEvolution)
    @jsonify
    def evolution(self):
        """
        Returns the optimizer evolution
        """
        evolution = Session.query(OptimizerEvolution)
        if 'source_se' in request.params and request.params['source_se']:
            evolution = evolution.filter(OptimizerEvolution.source_se == request.params['source_se'])
        if 'dest_se' in request.params and request.params['dest_se']:
            evolution = evolution.filter(OptimizerEvolution.dest_se == request.params['dest_se'])

        evolution = evolution.order_by(OptimizerEvolution.datetime.desc())

        return evolution[:50]
