"""
==========================
00. Fetch data on OpenfMRI
==========================

This script gives some basic code that can be adapted to fetch data.
"""

import os
from params import subjects_dir, data_path

pwd = os.getcwd()

print("data_path : %s" % data_path)

if not os.path.exists(data_path):
    data_path = os.path.abspath("data_demo")
    try:
        os.mkdir(data_path)
    except FileExistsError:
        print ('data_demo already exists')

os.chdir(data_path)

archive_dir = os.path.join(os.getcwd(), 'archive')

if not os.path.isdir(archive_dir):
    os.mkdir(archive_dir)

os.system('wget http://openfmri.s3.amazonaws.com/tarballs/ds117_R0.1.1_metadata.tgz')  # noqa: E501
os.system('tar xvzf ds117_R0.1.1_metadata.tgz')
os.system('mkdir metadata')
os.chdir(os.path.join(data_path, 'ds117'))
os.system('mv stimuli study_key.txt models README scan_key.txt model_key.txt listing.txt license.txt emptyroom ../metadata/')  # noqa: E501
os.chdir(data_path)
os.system('rmdir ds117')
os.system('mv ds117_R0.1.1_metadata.tgz archive/')


for i in range(1, 20):
    subject = "sub%03d" % i
    print("processing %s" % subject)
    fname = "ds117_R0.1.1_%s_raw.tgz" % subject
    url = "http://openfmri.s3.amazonaws.com/tarballs/" + fname
    if os.path.isdir(subject):
        continue
    if not os.path.exists(fname):
        os.system('wget %s' % url)
    os.system('tar xvzf %s' % fname)
    os.system('mv ds117/%s .' % subject)
    os.system('mv %s archive/' % fname)
    os.system('rmdir ds117')

os.chdir(pwd)

if not os.path.isdir(subjects_dir):
    os.mkdir(subjects_dir)
