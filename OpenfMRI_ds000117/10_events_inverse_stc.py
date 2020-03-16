"""
============================
04. Compute inverse solution
============================
The inverse solution pipeline performs source reconstruction starting from the
raw data specified by the user. The input raw data are epoched accordingly to
events specified in json file and created in script 03. The evoked datasets are
created by averaging the different conditions specified in json file.
"""

# Authors: Annalisa Pascarella <a.pascarella@iac.cnr.it>
# License: BSD (3-clause)

import nipype.pipeline.engine as pe

from params import data_path, subject_ids, subjects_dir, NJOBS
from ephypype.nodes import create_iterator, create_datagrabber


# from 03-extract_events
###############################################################################
# this is the dir where the cleaned raw data was saved

###############################################################################


path_ica = op.join(data_path,
                  'preprocessing_workflow','preproc_meeg_pipeline')



infosource = create_iterator(['subject_id'], [subject_ids])

###############################################################################
# and a node to grab data. The template_args in this node iterate upon
# the values in the infosource node

template_path = "_session_id_*_subject_id_%s/ica/run_*_sss_filt_ica.fif"
template_args = [['subject_id']]
infields = ['subject_id']

datasource = create_datagrabber(path_ica, template_path, template_args,
                                infields=infields)





def run_events_concatenate(list_ica_files):
    subject = "sub%03d" % subject_id
    print("processing subject: %s" % subject)
    in_path = op.join(data_path, subject, 'MEG')
    out_path = in_path

    raw_list = list()
    events_list = list()
    print("  Loading raw data")
    for run in range(1, 7):

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

    raw_file = op.join(out_path, '{}_sss_filt_ica-raw.fif'.format(subject))
    raw.save(raw_file, overwrite=True)

    event_file = op.join(
        out_path, '{}_sss_filt_ica-raw-eve.fif'.format(subject))
    mne.write_events(event_file, events)
    del raw_list
    del raw

    return raw_file, event_file


# from 05-group_average

def morph_stc(subject_id):
    subject = "sub%03d" % subject_id
    print("processing subject: %s" % subject)
    out_path = op.join(data_path, subject, 'MEG')

    # Morph STCs
    for k, condition in enumerate(conditions):
        stc = mne.read_source_estimate(
            op.join(out_path.format(subject),
            '{}_sss_filt_ica-raw-{}'.format(subject, k)))  # noqa

        print(op.join(out_path.format(subject),
                      '{}_sss_filt_ica-raw-{}'.format(subject, k)))
        morph = mne.compute_source_morph(
                        stc, subject_from=subject, subject_to='fsaverage',
                        subjects_dir=subjects_dir)
        stc_morphed = morph.apply(stc)
        stc_morphed.save(op.join(out_path,
                                 'mne_dSPM_inverse_morph-%s' % (condition)))




###############################################################################
# Read the parameters for inverse solution from a json file and print it

import json  # noqa
import pprint  # noqa
data = json.load(open("params_inverse.json"))
pprint.pprint({'inverse parameters': data})

events_id = data['events_id']
condition = data['condition']
events_file = data['events_file']
t_min = data['tmin']
t_max = data['tmax']
spacing = data['spacing']  # oct-6
snr = data['snr']
inv_method = data['method']  # dSPM
parc = data['parcellation']  # aparc
trans_fname = data['trans_fname']


###############################################################################
# Then, we create our workflow and specify the `base_dir` which tells
# nipype the directory in which to store the outputs.

# workflow directory within the `base_dir`
src_reconstruction_pipeline_name = 'source_reconstruction_' + \
    inv_method + '_' + parc.replace('.', '')

main_workflow = pe.Workflow(name=src_reconstruction_pipeline_name)
main_workflow.base_dir = data_path

###############################################################################
# Then we create a node to pass input filenames to DataGrabber from nipype

infosource = create_iterator(['subject_id'], [subject_ids])

###############################################################################
# and a node to grab data. The template_args in this node iterate upon
# the values in the infosource node

template_path = '*%s/MEG/%s_sss_filt_ica-raw.fif'
template_args = [['subject_id', 'subject_id']]
infields = ['subject_id']
datasource = create_datagrabber(data_path, template_path, template_args,
                                infields=infields)

###############################################################################
# Ephypype creates for us a pipeline which can be connected to these
# nodes we created. The inverse solution pipeline is implemented by the
# function ephypype.pipelines.preproc_meeg.create_pipeline_source_reconstruction,  # noqa
# thus to instantiate the inverse pipeline node, we import it and pass our
# parameters to it.
# The inverse pipeline contains three nodes that wrap the MNE Python functions
# that perform the source reconstruction steps.
#
# In particular, these three nodes are:
# * ephypype.interfaces.mne.LF_computation.LFComputation compute the
#   Lead Field matrix
# * ephypype.interfaces.mne.Inverse_solution.NoiseCovariance computes
#   the noise covariance matrix
# * ephypype.interfaces.mne.Inverse_solution.InverseSolution estimates
#   the time series of the neural sources on a set of dipoles grid

from ephypype.pipelines.fif_to_inv_sol import create_pipeline_source_reconstruction  # noqa
inv_sol_workflow = create_pipeline_source_reconstruction(
    data_path, subjects_dir, spacing=spacing, inv_method=inv_method,
    is_epoched=True, is_evoked=True, events_id=events_id, condition=condition,
    events_file=events_file, t_min=t_min, t_max=t_max,
    trans_fname=trans_fname, all_src_space=True, parc=parc)

###############################################################################
# We then connect the nodes two at a time. First, we connect the two outputs
# (subject_id and session_id) of the infosource node to the datasource node.
# So, these two nodes taken together can grab data.

main_workflow.connect(infosource, 'subject_id', datasource, 'subject_id')
# main_workflow.connect(infosource, 'session_id', datasource, 'session_id')

###############################################################################
# Similarly, for the inputnode of the preproc_workflow. Things will become
# clearer in a moment when we plot the graph of the workflow.

main_workflow.connect(infosource, 'subject_id',
                      inv_sol_workflow, 'inputnode.sbj_id')
main_workflow.connect(datasource, 'raw_file',
                      inv_sol_workflow, 'inputnode.raw')

###############################################################################
# To do so, we first write the workflow graph (optional)
main_workflow.write_graph(graph2use='colored')  # colored

# Finally, we are now ready to execute our workflow.

main_workflow.config['execution'] = {'remove_unnecessary_outputs': 'false'}

# Run workflow locally on 1 CPU
main_workflow.run(plugin='LegacyMultiProc', plugin_args={'n_procs': NJOBS})

###############################################################################
# The output is the source reconstruction matrix stored in the workflow
# directory defined by `base_dir`. This matrix can be used as input of
# the Connectivity pipeline.
