# Copyright 2016 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import os
import sys

def checkFileCode(filename):
    '''检查该文件的字符编码 避免读取字符串报错
    :param filename: 文件路径
    :return: 字符编码格式
    '''
    import codecs
    for encode in ['utf-8',
                   'gb2312',
                   'GB13000',
                   'gb18030',
                   'gbk',
                   'ISO-8859-1',
                   'ISO-8859-2',
                   'UTF-16',
                   'UTF-32',
                   'Error']:
        try:
            f = codecs.open(filename, mode='r', encoding=encode)
            u = f.read()
            f.close()
            return encode
        except:
            if encode == 'Error':
                return 'utf-8'

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
PY_UTILS = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', 'py_utils'))
PROTOBUF = os.path.abspath(os.path.join(
    SCRIPT_DIR, '..', 'third_party', 'protobuf'))
sys.path.append(PY_UTILS)
sys.path.append(PROTOBUF)
