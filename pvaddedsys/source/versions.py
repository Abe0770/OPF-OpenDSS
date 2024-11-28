import os
from pathlib import Path
import py_dss_interface
import pandas as pd
import numpy as np
import glob
import re
import matplotlib
import inspect
from copy import deepcopy

# Create a dictionary to store package names and versions
package_versions = {}

# Add each package and its version to the dictionary
package_versions['py_dss_interface'] = py_dss_interface.__version__ if hasattr(py_dss_interface, '__version__') else 'Unknown'
package_versions['pandas'] = pd.__version__
package_versions['numpy'] = np.__version__
package_versions['re'] = re.__version__ if hasattr(re, '__version__') else 'Builtin'
package_versions['matplotlib'] = matplotlib.__version__
# Print the versions of all imported packages
for package, version in package_versions.items():
    print(f"{package}=={version}")
