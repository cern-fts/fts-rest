#   Copyright notice:
#   Copyright  Members of the EMI Collaboration, 2013.
# 
#   See www.eu-emi.eu for details on the copyright holders
# 
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
# 
#       http://www.apache.org/licenses/LICENSE-2.0
# 
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

try:
    import simplejson as json
except:
    import json
import logging
from pylons import config,request

from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify, accept, get_input_as_dict
from fts3.model import OptimizerEvolution, Optimizer
from datetime import datetime
from fts3rest.lib.http_exceptions import *



class OptimizerController(BaseController):
    """
    Optimizer logging tables
    """

    @doc.return_type(bool)
    @jsonify
    def is_enabled(self):
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
    
    @doc.return_type(array_of=Optimizer)
    @jsonify
    def get_optimizer_values(self):
        """
        Returns the current number of actives and streams
        """
        optimizer = Session.query(Optimizer)
        if 'source_se' in request.params and request.params['source_se']:
            optimizer = optimizer.filter(Optimizer.source_se == request.params['source_se'])
        if 'dest_se' in request.params and request.params['dest_se']:
            optimizer = optimizer.filter(Optimizer.dest_se == request.params['dest_se'])

        optimizer = optimizer.order_by(Optimizer.datetime.desc())

        return optimizer
    
    @doc.response(400, 'Invalid values passed in the request')
    @jsonify
    def set_optimizer_values(self):
        """
        Set the number of actives and streams
        """
        input_dict = get_input_as_dict(request)
        source_se = input_dict.get('source_se', None)
        dest_se = input_dict.get('dest_se', None)
        
        current_time = datetime.utcnow()
        if not source_se or not dest_se:
            raise HTTPBadRequest('Missing source and/or destination')
        
        try:
            active = int(input_dict.get('active', 2))
        except Exception, e:
            raise HTTPBadRequest('Active must be an integer (%s)' % str(e))
        if active < 0:
            raise HTTPBadRequest('Active must be positive (%s)' % str(active))
        
        try:
            nostreams = int(input_dict.get('nostreams', 1))
        except Exception, e:
            raise HTTPBadRequest('Nostreams must be an integer (%s)' % str(e))
        if nostreams < 0:
            raise HTTPBadRequest('Nostreams must be positive (%s)' % str(nostreams))
        
        try:
            ema = float(input_dict.get('ema', 0))
        except Exception, e:
            raise HTTPBadRequest('Ema must be a float (%s)' % str(e))
        if ema < 0:
            raise HTTPBadRequest('Ema must be positive (%s)' % str(ema))

      
        optimizer = Optimizer(
            source_se=source_se,
            dest_se=dest_se,
            datetime = current_time,
            ema = ema,
            active=active,
            nostreams=nostreams
        )

        for key, value in input_dict.iteritems():
            setattr(optimizer, key, value)
                    
                
        Session.merge(optimizer)
        try:
            Session.commit()
        except:
            Session.rollback()
            raise

        return optimizer
    
