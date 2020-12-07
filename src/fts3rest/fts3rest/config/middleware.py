#   Copyright notice:
#   Copyright Members of the EMI Collaboration, 2013.
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

"""Pylons middleware initialization"""
from beaker.middleware import SessionMiddleware
from paste.cascade import Cascade
from paste.registry import RegistryManager
from paste.urlparser import StaticURLParser
from paste.deploy.converters import asbool
from pylons.middleware import ErrorHandler
from pylons.wsgiapp import PylonsApp
from routes.middleware import RoutesMiddleware

from fts3rest.lib.heartbeat import Heartbeat
from fts3rest.lib.openidconnect import oidc_manager
from fts3rest.lib.IAMTokenRefresher import IAMTokenRefresher
from fts3rest.lib.middleware.fts3auth import FTS3AuthMiddleware
from fts3rest.lib.middleware.error_as_json import ErrorAsJson
from fts3rest.lib.middleware.request_logger import RequestLogger
from fts3rest.lib.middleware.timeout import TimeoutHandler
from fts3rest.config.environment import load_environment

import logging

log = logging.getLogger(__name__)


def make_app(global_conf, full_stack=True, static_files=True, **app_conf):
    """Create a Pylons WSGI application and return it

    ``global_conf``
        The inherited configuration for this application. Normally from
        the [DEFAULT] section of the Paste ini file.

    ``full_stack``
        Whether this application provides a full WSGI stack (by default,
        meaning it handles its own exceptions and errors). Disable
        full_stack when this application is "managed" by another WSGI
        middleware.

    ``static_files``
        Whether this application serves its own static files; disable
        when another web server is responsible for serving them.

    ``app_conf``
        The application's local configuration. Normally specified in
        the [app:<name>] section of the Paste ini file (where <name>
        defaults to main).

    """
    # Configure the Pylons environment
    log.debug('loading environment')
    config = load_environment(global_conf, app_conf)

    # The Pylons WSGI app
    app = PylonsApp(config=config)

    # Routing/Session Middleware
    app = RoutesMiddleware(app, config['routes.map'])
    app = SessionMiddleware(app, config)

    # FTS3 authentication/authorization middleware
    app = FTS3AuthMiddleware(app, config)

    # Trap timeouts and the like
    app = TimeoutHandler(app, config)

    # Convert errors to a json representation
    app = ErrorAsJson(app, config)

    # Request logging
    app = RequestLogger(app, config)

    # Error handling
    if asbool(full_stack):
        # Handle Python exceptions
        app = ErrorHandler(app, global_conf, **config['pylons.errorware'])

    # Establish the Registry for this application
    app = RegistryManager(app)

    if asbool(static_files):
        # Serve static files
        static_app = StaticURLParser(config['pylons.paths']['static_files'])
        app = Cascade([static_app, app])
    app.config = config

    # Heartbeat thread
    Heartbeat('fts_rest', int(config.get('fts3.HeartBeatInterval', 60))).start()
    # Start OIDC clients
    if "fts3.Providers" in app.config and app.config["fts3.Providers"]:
        oidc_manager.setup(app.config)
        IAMTokenRefresher("fts_token_refresh_daemon", app.config).start()
        log.info("OpenID Connect support enabled.")
    else:
        log.info("OpenID Connect support disabled. Providers not found in config")

    return app
