"""
============================================
03. Extract events from the stimulus channel
============================================

The events are extracted from stimulus channel 'STI101'. The events are saved
to the subject's MEG directory.

For each subject, the different run are concatenated in one single raw file and
saved in the subject's MEG directory. We take the different run from the
preprocessing workflow directory, i.e. the cleaned raw data.
"""

import mne
import os.path as op

from mne.parallel import parallel_func

from params import data_path

###############################################################################
# this is the dir where the cleaned raw data was saved
ica_dir = op.join(data_path,
                  'preprocessing_workflow/preproc_meeg_pipeline/_session_id_%02d_subject_id_%s')  # noqa

###############################################################################


def run_events_concatenate(subject_id):
    subject = "sub%03d" % subject_id
    print("processing subject: %s" % subject)
    in_path = op.join(data_path, subject, 'MEG')
    out_path = in_path

    raw_list = list()
    events_list = list()
    print("  Loading raw data")
    for run in range(1, 7):
        run_fname = op.join(ica_dir % (run, subject),
                            'ica', 'run_%02d_sss_filt_ica.fif' % run)
        print(run_fname)
        raw = mne.io.read_raw_fif(run_fname, preload=True)
        mask = 4096 + 256  # mask for excluding high order bits
        events = mne.find_events(raw, stim_channel='STI101',
                                 consecutive='increasing', mask=mask,
                                 mask_type='not_and', min_duration=0.003)

        print("  S %s - R %s" % (subject, run))

        fname_events = op.join(out_path, 'run_%02d-eve.fif' % run)
        mne.write_events(fname_events, events)

        delay = int(round(0.0345 * raw.info['sfreq']))
        events[:, 0] = events[:, 0] + delay
        events_list.append(events)

        raw_list.append(raw)

    raw, events = mne.concatenate_raws(raw_list, events_list=events_list)
    raw.set_eeg_reference(projection=True)
    raw.save(op.join(out_path, '{}_sss_filt_ica-raw.fif'.format(subject)),
             overwrite=True)
    mne.write_events(op.join(
            out_path, '{}_sss_filt_ica-raw-eve.fif'.format(subject)), events)
    del raw_list
    del raw


###############################################################################
# Let us make the script parallel across subjects
# Here we use fewer N_JOBS to prevent potential memory problems
parallel, run_func, _ = parallel_func(run_events_concatenate, n_jobs=2)
parallel(run_func(subject_id) for subject_id in range(1, 20))
