# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import contextlib
import json
import logging
import os
import platform
import sys
import tempfile
import threading

DEVIL_DEFAULT_CONFIG_STR='''
{
  "config_type": "BaseConfig",
  "dependencies": {
    "aapt": {
      "cloud_storage_base_folder": "binary_dependencies",
      "cloud_storage_bucket": "chromium-telemetry",
      "file_info": {
        "linux2_x86_64": {
          "cloud_storage_hash": "87bd288daab30624e41faa62aa2c1d5bac3e60aa",
          "download_path": "../bin/deps/linux2/x86_64/bin/aapt"
        }
      }
    },
    "adb": {
      "cloud_storage_base_folder": "binary_dependencies",
      "cloud_storage_bucket": "chromium-telemetry",
      "file_info": {
        "linux2_x86_64": {
          "cloud_storage_hash": "8bd43e3930f6eec643d5dc64cab9e5bb4ddf4909",
          "download_path": "../bin/deps/linux2/x86_64/bin/adb"
        }
      }
    },
    "android_build_tools_libc++": {
      "cloud_storage_base_folder": "binary_dependencies",
      "cloud_storage_bucket": "chromium-telemetry",
      "file_info": {
        "linux2_x86_64": {
          "cloud_storage_hash": "9b986774ad27288a6777ebfa9a08fd8a52003008",
          "download_path": "../bin/deps/linux2/x86_64/lib64/libc++.so"
        }
      }
    },
    "chromium_commands": {
      "cloud_storage_base_folder": "binary_dependencies",
      "cloud_storage_bucket": "chromium-telemetry",
      "file_info": {
        "linux2_x86_64": {
          "cloud_storage_hash": "4e22f641e4757309510e8d9f933f5aa504574ab6",
          "download_path": "../bin/deps/linux2/x86_64/lib.java/chromium_commands.dex.jar"
        }
      }
    },
    "dexdump": {
      "cloud_storage_base_folder": "binary_dependencies",
      "cloud_storage_bucket": "chromium-telemetry",
      "file_info": {
        "linux2_x86_64": {
          "cloud_storage_hash": "c3fdf75afe8eb4062d66703cb556ee1e2064b8ae",
          "download_path": "../bin/deps/linux2/x86_64/bin/dexdump"
        }
      }
    },
    "empty_system_webview": {
      "cloud_storage_base_folder": "binary_dependencies",
      "cloud_storage_bucket": "chromium-telemetry",
      "file_info": {
        "android_arm64-v8a": {
          "cloud_storage_hash": "34e583c631a495afbba82ce8a1d4f9b5118a4411",
          "download_path": "../bin/deps/android/arm64-v8a/apks/EmptySystemWebView.apk"
        },
        "android_armeabi-v7a": {
          "cloud_storage_hash": "220ff3ba1a6c3c81877997e32784ffd008f293a5",
          "download_path": "../bin/deps/android/armeabi-v7a/apks/EmptySystemWebView.apk"
        }
      }
    },
    "fastboot": {
      "cloud_storage_base_folder": "binary_dependencies",
      "cloud_storage_bucket": "chromium-telemetry",
      "file_info": {
        "linux2_x86_64": {
          "cloud_storage_hash": "db9728166f182800eb9d09e9f036d56e105e8235",
          "download_path": "../bin/deps/linux2/x86_64/bin/fastboot"
        }
      }
    },
    "forwarder_device": {
      "cloud_storage_base_folder": "binary_dependencies",
      "cloud_storage_bucket": "chromium-telemetry",
      "file_info": {
        "android_arm64-v8a": {
          "cloud_storage_hash": "f222268d8442979240d1b18de00911a49e548daa",
          "download_path": "../bin/deps/android/arm64-v8a/bin/forwarder_device"
        },
        "android_armeabi-v7a": {
          "cloud_storage_hash": "c15267bf01c26eb0aea4f61c780bbba460c5c981",
          "download_path": "../bin/deps/android/armeabi-v7a/bin/forwarder_device"
        }
      }
    },
    "forwarder_host": {
      "cloud_storage_base_folder": "binary_dependencies",
      "cloud_storage_bucket": "chromium-telemetry",
      "file_info": {
        "linux2_x86_64": {
          "cloud_storage_hash": "8fe69994b670f028484eed475dbffc838c8a57f7",
          "download_path": "../bin/deps/linux2/x86_64/forwarder_host"
        }
      }
    },
    "md5sum_device": {
      "cloud_storage_base_folder": "binary_dependencies",
      "cloud_storage_bucket": "chromium-telemetry",
      "file_info": {
        "android_arm64-v8a": {
          "cloud_storage_hash": "4e7d2dedd9c6321fdc152b06869e09a3c5817904",
          "download_path": "../bin/deps/android/arm64-v8a/bin/md5sum_device"
        },
        "android_armeabi-v7a": {
          "cloud_storage_hash": "39fd90af0f8828202b687f7128393759181c5e2e",
          "download_path": "../bin/deps/android/armeabi-v7a/bin/md5sum_device"
        },
        "android_x86": {
          "cloud_storage_hash": "d5cf42ab5986a69c31c0177b0df499d6bf708df6",
          "download_path": "../bin/deps/android/x86/bin/md5sum_device"
        }
      }
    },
    "md5sum_host": {
      "cloud_storage_base_folder": "binary_dependencies",
      "cloud_storage_bucket": "chromium-telemetry",
      "file_info": {
        "linux2_x86_64": {
          "cloud_storage_hash": "4db5bd5e9bea8880d8bf2caa59d0efb0acc19f74",
          "download_path": "../bin/deps/linux2/x86_64/bin/md5sum_host"
        }
      }
    },
    "split-select": {
      "cloud_storage_base_folder": "binary_dependencies",
      "cloud_storage_bucket": "chromium-telemetry",
      "file_info": {
        "linux2_x86_64": {
          "cloud_storage_hash": "c116fd0d7ff089561971c078317b75b90f053207",
          "download_path": "../bin/deps/linux2/x86_64/bin/split-select"
        }
      }
    }
  }
}

'''
CATAPULT_ROOT_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..'))
DEPENDENCY_MANAGER_PATH = os.path.join(
    CATAPULT_ROOT_PATH, 'dependency_manager')
PYMOCK_PATH = os.path.join(
    CATAPULT_ROOT_PATH, 'third_party', 'mock')


@contextlib.contextmanager
def SysPath(path):
  sys.path.append(path)
  yield
  if sys.path[-1] != path:
    sys.path.remove(path)
  else:
    sys.path.pop()

with SysPath(DEPENDENCY_MANAGER_PATH):
  import dependency_manager  # pylint: disable=import-error

_ANDROID_BUILD_TOOLS = {'aapt', 'dexdump', 'split-select'}

_DEVIL_DEFAULT_CONFIG = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'devil_dependencies.json'))
if not os.path.isfile(_DEVIL_DEFAULT_CONFIG):
  _DEVIL_DEFAULT_CONFIG = os.path.sep.join(['config','devil_dependencies.json'])
  if not os.path.isfile(_DEVIL_DEFAULT_CONFIG):
    os.mkdir(os.path.dirname(_DEVIL_DEFAULT_CONFIG))
    f = open(_DEVIL_DEFAULT_CONFIG, mode='w')
    f.write(DEVIL_DEFAULT_CONFIG_STR)
    f.close()

_LEGACY_ENVIRONMENT_VARIABLES = {
  'ADB_PATH': {
    'dependency_name': 'adb',
    'platform': 'linux2_x86_64',
  },
  'ANDROID_SDK_ROOT': {
    'dependency_name': 'android_sdk',
    'platform': 'linux2_x86_64',
  },
}


def EmptyConfig():
  return {
    'config_type': 'BaseConfig',
    'dependencies': {}
  }


def LocalConfigItem(dependency_name, dependency_platform, dependency_path):
  if isinstance(dependency_path, basestring):
    dependency_path = [dependency_path]
  return {
    dependency_name: {
      'file_info': {
        dependency_platform: {
          'local_paths': dependency_path
        },
      },
    },
  }


def _GetEnvironmentVariableConfig():
  env_config = EmptyConfig()
  path_config = (
      (os.environ.get(k), v)
      for k, v in _LEGACY_ENVIRONMENT_VARIABLES.iteritems())
  path_config = ((p, c) for p, c in path_config if p)
  for p, c in path_config:
    env_config['dependencies'].update(
        LocalConfigItem(c['dependency_name'], c['platform'], p))
  return env_config


class _Environment(object):

  def __init__(self):
    self._dm_init_lock = threading.Lock()
    self._dm = None
    self._logging_init_lock = threading.Lock()
    self._logging_initialized = False

  def Initialize(self, configs=None, config_files=None):
    """Initialize devil's environment from configuration files.

    This uses all configurations provided via |configs| and |config_files|
    to determine the locations of devil's dependencies. Configurations should
    all take the form described by py_utils.dependency_manager.BaseConfig.
    If no configurations are provided, a default one will be used if available.

    Args:
      configs: An optional list of dict configurations.
      config_files: An optional list of files to load
    """

    # Make sure we only initialize self._dm once.
    with self._dm_init_lock:
      if self._dm is None:
        if configs is None:
          configs = []

        env_config = _GetEnvironmentVariableConfig()
        if env_config:
          configs.insert(0, env_config)
        self._InitializeRecursive(
            configs=configs,
            config_files=config_files)
        assert self._dm is not None, 'Failed to create dependency manager.'

  def _InitializeRecursive(self, configs=None, config_files=None):
    # This recurses through configs to create temporary files for each and
    # take advantage of context managers to appropriately close those files.
    # TODO(jbudorick): Remove this recursion if/when dependency_manager
    # supports loading configurations directly from a dict.
    if configs:
      with tempfile.NamedTemporaryFile(delete=False) as next_config_file:
        try:
          next_config_file.write(json.dumps(configs[0]))
          next_config_file.close()
          self._InitializeRecursive(
              configs=configs[1:],
              config_files=[next_config_file.name] + (config_files or []))
        finally:
          if os.path.exists(next_config_file.name):
            os.remove(next_config_file.name)
    else:
      config_files = config_files or []
      if 'DEVIL_ENV_CONFIG' in os.environ:
        config_files.append(os.environ.get('DEVIL_ENV_CONFIG'))
      config_files.append(_DEVIL_DEFAULT_CONFIG)

      self._dm = dependency_manager.DependencyManager(
          [dependency_manager.BaseConfig(c) for c in config_files])

  def InitializeLogging(self, log_level, formatter=None, handler=None):
    if self._logging_initialized:
      return

    with self._logging_init_lock:
      if self._logging_initialized:
        return

      formatter = formatter or logging.Formatter(
          '%(threadName)-4s  %(message)s')
      handler = handler or logging.StreamHandler(sys.stdout)
      handler.setFormatter(formatter)

      devil_logger = logging.getLogger('devil')
      devil_logger.setLevel(log_level)
      devil_logger.propagate = False
      devil_logger.addHandler(handler)

      import py_utils.cloud_storage
      lock_logger = py_utils.cloud_storage.logger
      lock_logger.setLevel(log_level)
      lock_logger.propagate = False
      lock_logger.addHandler(handler)

      self._logging_initialized = True

  def FetchPath(self, dependency, arch=None, device=None):
    if self._dm is None:
      self.Initialize()
    if dependency in _ANDROID_BUILD_TOOLS:
      self.FetchPath('android_build_tools_libc++', arch=arch, device=device)
    return self._dm.FetchPath(dependency, GetPlatform(arch, device))

  def LocalPath(self, dependency, arch=None, device=None):
    if self._dm is None:
      self.Initialize()
    return self._dm.LocalPath(dependency, GetPlatform(arch, device))

  def PrefetchPaths(self, dependencies=None, arch=None, device=None):
    return self._dm.PrefetchPaths(
        GetPlatform(arch, device), dependencies=dependencies)


def GetPlatform(arch=None, device=None):
  if arch or device:
    return 'android_%s' % (arch or device.product_cpu_abi)
  return '%s_%s' % (sys.platform, platform.machine())


config = _Environment()

