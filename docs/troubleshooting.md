Troubleshooting
===============

The EvalException middleware is not usable in a multi-process environment
-------------------------------------------------------------------------
Set `debug = False` in /etc/fts3/fts3rest.ini and restart.

FTS3 Rest behind DNS load balancing
-----------------------------------
If you have several FTS3 instances behind a DNS load balancer, then you have two options

### Use the same certificate for all instances
Generate one single certificate with the public name, and share them between the different hosts.
This solution is suboptimal, since then each host will not be accessible separately.

### Use alternative names
Issue one certificate per host, with the subject matching the host name, and add to all of them a [subject alternative name](http://en.wikipedia.org/wiki/SubjectAltName) that matches the balanced name.

FTS3 RESTful CLI says "X509v3 extensions disabled!"
---------------------------------------------------
The X509v3 extension handling in the python26-m2crypto shipped in EPEL5 is broken, so it has been disabled.
If you are getting this error in some other platform, please, [let us know](fts-support@cern.ch)!
