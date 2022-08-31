"""
Sabueso
This must be a short description of the project
"""

# Handle versioneer
from ._version import get_versions
versions = get_versions()
__version__ = versions['version']
__git_revision__ = versions['full-revisionid']
del get_versions, versions


# Auxiliary libraries
from ._pyunitwizard import pyunitwizard
from ._evidence import evidence

# Add imports here
from . import protein
from . import database

