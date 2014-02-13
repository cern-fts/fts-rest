from datetime import datetime, timedelta
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3.model import OptimizerEvolution, Optimizer
from pylons import config, request


class OptimizerController(BaseController):
    """
    Optimizer logging tables
    """

    @jsonify
    def isEnabled(self):
        """
        Indicates if the optimizer is enabled in the server
        """
        return  {
                'enabled': config['fts3.Optimizer'],
                '_links':  {
                            'curies': [{'href': 'https://svnweb.cern.ch/trac/fts3', 'name': 'fts'}],
                            'fts:evolution':  {
                                              'href': '/optimizer/evolution{?source_se,dest_se}',
                                              'title': 'Evolution',
                                              'templated': True
                                              },
                            'fts:snapshot': {'href': '/optimizer/snapshot', 'title': 'Snapshot'}
                           }
                }

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

    @jsonify
    def snapshot(self):
        notBefore = datetime.utcnow() - timedelta(hours = 48)
        snapshot = Session.query(Optimizer)
        snapshot = snapshot.filter(Optimizer.datetime >= notBefore)
        snapshot = snapshot.filter(Optimizer.throughput != None)

        if 'source_se' in request.params and request.params['source_se']:
            snapshot = snapshot.filter(Optimizer.source_se == request.params['source_se'])
        if 'dest_se' in request.params and request.params['dest_se']:
            snapshot = snapshot.filter(Optimizer.dest_se == request.params['dest_se'])

        snapshot = snapshot.order_by(Optimizer.datetime.desc())

        return snapshot.all()
