"""
=================================
05. Group average on source level
=================================

Source estimates are morphed to the ``fsaverage`` brain.
"""

import mne
import os.path as op

from mne.parallel import parallel_func
from params import meg_dir, subjects_dir, NJOBS, conditions


def morph_stc(subject_id):
    subject = "sub%03d" % subject_id
    print("processing subject: %s" % subject)
    data_path = op.join(meg_dir, 'ds117', subject, 'MEG')

    # Morph STCs
    for k, condition in enumerate(conditions):
        stc = mne.read_source_estimate(
            op.join(data_path.format(subject),
            '{}_sss_filt_ica-raw-{}'.format(subject, k)))  # noqa

        print(op.join(data_path.format(subject),
                      '{}_sss_filt_ica-raw-{}'.format(subject, k)))
        morph = mne.compute_source_morph(
                        stc, subject_from=subject, subject_to='fsaverage',
                        subjects_dir=subjects_dir)
        stc_morphed = morph.apply(stc)
        stc_morphed.save(op.join(data_path,
                                 'mne_dSPM_inverse_morph-%s' % (condition)))


parallel, run_func, _ = parallel_func(morph_stc, n_jobs=NJOBS)
parallel(run_func(subject_id) for subject_id in range(1, 20))
