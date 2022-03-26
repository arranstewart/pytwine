"""
version of the package.
"""

version_info = (0, 1, 0)

def create_valid_version(ver_info):
  '''
  Return a version string from version_info.
  '''

  return ".".join( [str(c) for c in ver_info] )

__version__ = create_valid_version(version_info)
