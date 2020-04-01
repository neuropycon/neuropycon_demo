"""
==========================
00. Fetch data on OpenfMRI
==========================

This script gives some basic code that can be adapted to fetch data.
"""

import os
import json

rel_path = os.path.split(os.path.realpath(__file__))[0]
print(rel_path)


params = json.load(open(os.path.join(rel_path, "params.json")))

print(params["general"])

subjects_dir = params["general"]["subjects_dir"]
subject_ids = params["general"]["subject_ids"]

if "data_path" in params["general"].keys():
    data_path = params["general"]["data_path"]
else:
    data_path = os.path.expanduser("")

print (data_path, subjects_dir, subject_ids)

# creating data_demo
data_path = os.path.join(data_path, "data_demo")

print("data_path : %s" % data_path)

if not os.path.exists(data_path):
    try:
        os.mkdir(data_path)
    except FileExistsError:
        print ('data_demo already exists')

os.chdir(data_path)

# fetch data

#os.system('wget http://openfmri.s3.amazonaws.com/tarballs/ds117_R0.1.1_metadata.tgz')  # noqa: E501
#os.system('tar xvzf ds117_R0.1.1_metadata.tgz')
#os.system('mkdir metadata')
#os.chdir(os.path.join(data_path, 'ds117'))
#os.system('mv stimuli study_key.txt models README scan_key.txt model_key.txt listing.txt license.txt emptyroom ../metadata/')  # noqa: E501
#os.chdir(data_path)
#os.system('rmdir ds117')

#downloding subject data
for subject in subject_ids:
    print("processing %s" % subject)
    fname = "ds117_R0.1.1_%s_raw.tgz" % subject
    url = "http://openfmri.s3.amazonaws.com/tarballs/" + fname
    if os.path.isdir(subject):
        continue
    if not os.path.exists(fname):
        os.system('wget %s' % url)
    os.system('tar xvzf %s' % fname)
    os.system('mv ds117/%s .' % subject)
    #os.system('mv %s archive/' % fname)
    os.system('rmdir ds117')

subjects_dir = os.path.join(data_path, subjects_dir)

if not os.path.isdir(subjects_dir):
    os.mkdir(subjects_dir)

