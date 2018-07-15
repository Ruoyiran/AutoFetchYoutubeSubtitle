# -*- coding:utf-8 -*-
"""
@version: 1.0
@author: Roy
@contact: ruoyi_ran@foxmail.com
@file: utils.py
@time: 2018/7/15 17:53
"""
import os
import shutil
import zipfile


def unzip_file(zip_file_path):
    """unzip zip file"""
    root_dir_path, file_name = os.path.split(zip_file_path)
    dir_name = os.path.splitext(file_name)[0]
    dir_path = os.path.join(root_dir_path, dir_name)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    zip_file = zipfile.ZipFile(zip_file_path)
    name_list = zip_file.namelist() or list()
    for name in name_list:
        zip_file.extract(name, dir_path)
    zip_file.close()
    return dir_path, name_list


def remove_dir(dir_path):
    if not os.path.exists(dir_path):
        return False
    shutil.rmtree(dir_path)
