Developer notes
===============
This document briefly summarizes some points that can be of interest for anyone modifying the FTS3 RESTful API.

**It is not intended for developers of client applications**. For them we have the
[auto generated API documentation](api.md), the list of [curl examples](api-curl.md) or the [easy bindings](easy/README.md).

Quick references
----------------
A basic knowledge of git is obviously required. There are plenty of [tutorials](https://www.google.ch/search?q=git+tutorial) out there.

The service is written using [Pylons 0.9.7](https://pylons-webframework.readthedocs.org/en/v0.9.7/)

The database abstraction is done by [SQLAlchemy 0.5.5](http://docs.sqlalchemy.org/en/rel_0_5/)

There are a bunch of tests written using Python's [unittest](https://docs.python.org/2/library/unittest.html) module, and they can be executed
automatically with [nosetests](https://nose.readthedocs.org/en/latest/).

Branches
--------

### Main branches
#### develop
Integrated development version. Should be in a consistent state, but not necessarely stable.
This means, new features go here, and they should be in a workable state.

#### stage
Pre-release branch. Only bugfixes. Runs on the FTS3 pilot service.

#### master
__Stable branch__. Only critical bugfixes. Runs on the FTS3 production service.

### Other branches
develop should be consistent and workable. For big changesets, you can keep them in a separate branch, and merge them into
develop when they are ready (remember to rebase first).
You don't need to keep these branches in the remote repositories.

### Remotes
There are two clones of this repository:
* https://github.com/cern-it-sdc-id/fts3-rest
* https://git.cern.ch/web/fts3-rest.git

Please, keep master and stage synchronized in both.

Release cycle
-------------
1. New features are commited into develop. Big new features go into their own branch and later merged into develop.
    * Keep documentation up to date
2. When develop is ready for being a release candidate, merge develop into stage.
    * Increase the version of develop after this!
3. When stage is stable and ready for release
    1. Make sure the documentation is up to date
    2. Write release notes for the new version (contained in docs/releases)
    3. Merge into master
    4. Tag, and mark version as released in JIRA (move any remaining tickets to the next release)

Guidelines
----------

This is just a small recopilatory of some guidelines that I consider worth considering when working on this project.
They don't have to strictly be followed. Nevertheless, they are handy.

### A new source file is added
Remember to add the copyright notice

```
#   Copyright notice:
#   Copyright  CERN, 2014.
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
```

### A wild bug appears!
If you find a bug, or someone reports one, it is helpful to write a regression test _before_ actually doing the fix.
So write the tests reproducing the buggy behavior, execute, and make sure they do fail.
Once the bug has a test that automatically reproduces it, you do the fix. Re-run the test, and now it should pass.

I would recommend to run the whole test suite afterwards, to make sure the fix didn't break anything else!
Precisely this is why I recommend writting a test. It will ensure this bug doesn't come back after some future modifications.

Remind creating a ticket in the JIRA tracker and linking it to the proper version!

### A new feature is added
Basically, the same idea applies. Write some tests for the new functionality, so you know you are achieving what you are expecting.

JIRA tickets are mandatory in this case. Otherwise, tracking release changes is hard.

### Logging
Python's [logging](https://docs.python.org/2/library/logging.html) is really handy and powerful. Use it!

P.S I recognise I don't use it as much as I should.

### Keep history clean and tidy
1. Write meaningful commit messages
2. Specify any relevant JIRA ticket in the commit
3. Avoid multipurpose jumbo commits
    * They should not contain unrelated changes (i.e. two bug fixes in one commit, bad)
4. Before pushing, group related commits (yes, [you can do this with git](http://stackoverflow.com/questions/6884022/collapsing-a-group-of-commits-into-one-on-git))
    * If you have two commits for one single bug fix, try grouping them whenever it makes sense.

FAQ
---

### Configuration files
* In a normally installed service, `/etc/fts3/fts3rest.ini`
* If you are running the tests with nosetests, then `src/fts3rest/test.ini` is used instead

### How do I run the tests
```bash
cd src/fts3rest/
nosetests -x
```

That's it. For the tests, a SQLite database (/tmp/fts3.db) is used, so it is safe to run them as many times as you want.
The option `-x` lets nosetests know that it should stop running as soon as it encounters an error, so you can omit it.

If you have `nosestests1.1` installed, you can run the test suite as follows

```bash
cd src/fts3rest/
nosetests1.1 --with-coverage --cover-package=fts3rest
```

That will give coverage information. This is, which lines have been triggered by the tests.

### Can I see the queries that SQLAlchemy runs?
Yes, you can. Just edit the relevant configuration file, look for `[logger_sqlalchemy]` and set the level to INFO.
The queries will be dumped into the log file.
