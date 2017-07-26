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
        rationale = input_dict.get('rationale', None)
        
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
            diff = int(input_dict.get('diff', 1))
        except Exception, e:
            raise HTTPBadRequest('Diff must be an integer (%s)' % str(e))
        if diff < 0:
            raise HTTPBadRequest('Diff must be positive (%s)' % str(diff))
        try:
            actual_active = int(input_dict.get('actual_active', 1))
        except Exception, e:
            raise HTTPBadRequest('Actual_active must be an integer (%s)' % str(e))
        if actual_active < 0:
            raise HTTPBadRequest('Actual_active must be positive (%s)' % str(actual_active))
        try:
            queue_size = int(input_dict.get('queue_size', 1))
        except Exception, e:
            raise HTTPBadRequest('Queue_size must be an integer (%s)' % str(e))
        if queue_size < 0:
            raise HTTPBadRequest('Queue_size must be positive (%s)' % str(queue_size))
        try:
            ema = float(input_dict.get('ema', 0))
        except Exception, e:
            raise HTTPBadRequest('Ema must be a float (%s)' % str(e))
        if ema < 0:
            raise HTTPBadRequest('Ema must be positive (%s)' % str(ema))
        try:
            throughput = float(input_dict.get('throughput', 0))
        except Exception, e:
            raise HTTPBadRequest('Throughput must be a float (%s)' % str(e))
        if throughput < 0:
            raise HTTPBadRequest('Throughput must be positive (%s)' % str(throughput))
        try:
            success = float(input_dict.get('success', 0))
        except Exception, e:
            raise HTTPBadRequest('Success must be a float (%s)' % str(e))
        if success < 0:
            raise HTTPBadRequest('Success must be positive (%s)' % str(success))
        try:
            filesize_avg = float(input_dict.get('filesize_avg', 0))
        except Exception, e:
            raise HTTPBadRequest('Filesize_avg must be a float (%s)' % str(e))
        if filesize_avg < 0:
            raise HTTPBadRequest('Filesize_avg must be positive (%s)' % str(filesize_avg))
        try:
            filesize_stddev = float(input_dict.get('filesize_stddev', 0))
        except Exception, e:
            raise HTTPBadRequest('Filesize_stddev must be a float (%s)' % str(e))
        if filesize_stddev < 0:
            raise HTTPBadRequest('Filesize_stddev must be positive (%s)' % str(filesize_stddev))
    
        optimizer = Optimizer(
            source_se=source_se,
            dest_se=dest_se,
            datetime = current_time,
            ema = ema,
            active=active,
            nostreams=nostreams
        )
        evolution = OptimizerEvolution(
            source_se=source_se,
            dest_se=dest_se,
            datetime = current_time,
            ema = ema,
            active=active,
            throughput=throughput,
            success=success,
            rationale=rationale,
            diff=diff,
            actual_active=actual_active,
            queue_size=queue_size,
            filesize_avg=filesize_avg,
            filesize_stddev=filesize_stddev
        )
                                    
        

        for key, value in input_dict.iteritems():
            setattr(evolution, key, value)
        for key, value in input_dict.iteritems():
            setattr(optimizer, key, value)

        Session.merge(evolution)
        Session.merge(optimizer)
        try:
            Session.commit()
        except:
            Session.rollback()
            raise

        return (evolution, optimizer)
    
