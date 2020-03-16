"""
==========================
00. Fetch data on OpenfMRI
==========================

This script gives some basic code that can be adapted to fetch data.
"""

import os
import json

#from params import subjects_dir, data_path


import json  # noqa
import pprint  # noqa
params = json.load(open("params.json"))
print(params)
subjects_dir = params["subjects_dir"]


pwd = os.getcwd()


rel_path = op.join(op.split(__file__)[0])

params = json.load(open(os.path.join(rel_path, "params.json")))

data_path = os.path.join(rel_path, "data_demo")

print("data_path : %s" % data_path)

if not os.path.exists(data_path):
    try:
        os.mkdir(data_path)
    except FileExistsError:
        print ('data_demo already exists')

os.chdir(data_path)

os.system('wget http://openfmri.s3.amazonaws.com/tarballs/ds117_R0.1.1_metadata.tgz')  # noqa: E501
os.system('tar xvzf ds117_R0.1.1_metadata.tgz')
os.system('mkdir metadata')
os.chdir(os.path.join(data_path, 'ds117'))
os.system('mv stimuli study_key.txt models README scan_key.txt model_key.txt listing.txt license.txt emptyroom ../metadata/')  # noqa: E501
os.chdir(data_path)
os.system('rmdir ds117')

for i in range(1, 4):
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

subjects_dir = os.path.join(data_path, subjects_dir)

if not os.path.isdir(subjects_dir):
    os.mkdir(subjects_dir)
