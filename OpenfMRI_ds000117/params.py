"""
Created on Wed Dec  4 06:33:33 2019

@author: pasca
"""
import os
import getpass
import numpy as np


is_nii = True  # True if you have MRI files in nii format

# TODO -> define all important dir (i.e set sbj dir path, i.e. where the
#         FreeSurfer folders are)
if getpass.getuser() == 'pasca':
    meg_dir = '/home/pasca/Tools/python/Projets/mne-biomag-group-demo/'

    subjects_dir = os.path.join(meg_dir, 'FSF')
    MRI_path = meg_dir
    data_path = os.path.join(meg_dir, 'ds117')

    NJOBS = 4

elif getpass.getuser() == 'karim':
    meg_dir = '/home/karim/Tools/python/Projets/mne-biomag-group-demo/'

    subjects_dir = os.path.join(meg_dir, 'subjects')
    MRI_path = os.path.join(meg_dir, 'ds117')
    data_path = os.path.join(meg_dir, 'ds117')

    NJOBS = 4

else:
    main_path = ''
    subjects_dir = ''
    MRI_path = ''
    data_path = ''

    NJOBS = 4

# subjects list and session numbering
subject_ids = ['sub001', 'sub002', 'sub003', 'sub004', 'sub005', 'sub006',
               'sub007', 'sub008', 'sub009', 'sub010', 'sub011', 'sub012',
               'sub013', 'sub014', 'sub015', 'sub016', 'sub017', 'sub018',
               'sub019']
session_ids = ['01', '02', '03', '04', '05', '06']
# Subjects that are known to be bad from the publication
exclude_subjects = [1, 5, 16]  # Excluded subjects

# dir names in subjects_dir for Freesurfer workflow (01-smri_reconall.py)
FS_WF_name = "segmentation_workflow"
BEM_WF_name = "watershed_bem"
MAIN_WF_name = "FS_workflow"

data_type = 'fif'

fsaverage_vertices = [np.arange(10242), np.arange(10242)]
smooth = 10


conditions = ['famous', 'scrambled', 'unfamiliar']
