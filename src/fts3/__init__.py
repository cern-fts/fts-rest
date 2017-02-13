import pkg_resources

try:
    __version__ = pkg_resources.get_distribution("fts3").version
except pkg_resources.DistributionNotFound:
    __version__ = '3.x.x'
