import os, sys

# Set up the path so imports can be done from fts3rest
wd = os.path.dirname(__file__) + '/../../'
if wd not in sys.path:
    sys.path.append(wd)
    