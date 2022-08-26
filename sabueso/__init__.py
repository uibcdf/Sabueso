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

__documentation_web__ = 'https://www.uibcdf.org/Sabueso'
__github_web__ = 'https://github.com/uibcdf/Sabueso'
__github_issues_web__ = __github_web__ + '/issues'

from ._pyunitwizard import pyunitwizard

# Add imports here
from ._evidence import evidence

#from . import protein
from . import database
#from . import file

