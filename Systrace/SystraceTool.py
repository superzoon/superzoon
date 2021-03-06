#!/usr/bin/env python

# Copyright (c) 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os
import sys
from systrace import run_systrace

def RemoveAllStalePycFiles(base_dir):
  """Scan directories for old .pyc files without a .py file and delete them."""
  for dirname, _, filenames in os.walk(base_dir):
    if '.git' in dirname:
      continue
    for filename in filenames:
      root, ext = os.path.splitext(filename)
      if ext != '.pyc':
        continue

      pyc_path = os.path.join(dirname, filename)
      py_path = os.path.join(dirname, root + '.py')

      try:
        if not os.path.exists(py_path):
          os.remove(pyc_path)
      except OSError:
        # Wrap OS calls in try/except in case another process touched this file.
        pass

    try:
      os.removedirs(dirname)
    except OSError:
      # Wrap OS calls in try/except in case another process touched this dir.
      pass


if __name__ == '__main__':
  import win32api
  import win32con
  RemoveAllStalePycFiles(os.path.dirname(__file__))
  sys.exit(run_systrace.main())
