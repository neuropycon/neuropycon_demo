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

#from params import data_path, subject_ids, subjects_dir, NJOBS
from ephypype.nodes import create_iterator, create_datagrabber

from nipype.interfaces.utility import Function
from ephypype.pipelines.fif_to_inv_sol import create_pipeline_source_reconstruction  # noqa


### relative path
rel_path = op.join(op.split(__file__)[0])
data_path = os.path.join(rel_path, "data_demo")
subjects_dir = os.path.join(data_path, subjects_dir)

# from 03-extract_events
###############################################################################



#def run_events_concatenate(subject_id, ica_dir):

    ## could be added in a node to come
    #mask = 4096 + 256  # mask for excluding high order bits
    #conv_freq = 0.0345
    #min_duration = 0.003


    #subject = "sub%03d" % subject_id
    #print("processing subject: %s" % subject)
    #in_path = op.join(data_path, subject, 'MEG')
    #out_path = in_path

    #raw_list = list()
    #events_list = list()
    #print("  Loading raw data")
    #for run in range(1, 7):
        #run_fname = op.join(ica_dir % (run, subject),
                            #'ica', 'run_%02d_sss_filt_ica.fif' % run)
        #print(run_fname)
        #raw = mne.io.read_raw_fif(run_fname, preload=True)
        #events = mne.find_events(raw, stim_channel='STI101',
                                 #consecutive='increasing', mask=mask,
                                 #mask_type='not_and', min_duration=0.003)

        #print("  S %s - R %s" % (subject, run))

        #fname_events = op.join(out_path, 'run_%02d-eve.fif' % run)
        #mne.write_events(fname_events, events)

        #delay = int(round(conv_freq * raw.info['sfreq']))
        #events[:, 0] = events[:, 0] + delay
        #events_list.append(events)

        #raw_list.append(raw)

    #raw, events = mne.concatenate_raws(raw_list, events_list=events_list)
    #raw.set_eeg_reference(projection=True)
    #raw.save(op.join(out_path, '{}_sss_filt_ica-raw.fif'.format(subject)),
             #overwrite=True)
    #mne.write_events(op.join(
            #out_path, '{}_sss_filt_ica-raw-eve.fif'.format(subject)), events)
    #del raw_list
    #del raw



def run_events_concatenate(list_ica_files,
                           subject_id, data_path):

    subject = "sub%03d" % subject_id
    print("processing subject: %s" % subject)
    out_path = op.join(data_path, subject, 'MEG')
    #out_path = in_path

    raw_list = list()
    events_list = list()
    fname_events_files = []

    print("  Loading raw data")
    for i,run_fname in enumerate(list_ica_files):
        run = i+1

        print(run_fname)
        raw = mne.io.read_raw_fif(run_fname, preload=True)
          # mask for excluding high order bits
        events = mne.find_events(raw, stim_channel='STI101',
                                 consecutive='increasing', mask=mask,
                                 mask_type='not_and', min_duration=min_duration)

        print("  S %s - R %s" % (subject, run))

        fname_events = op.join(out_path, 'run_%02d-eve.fif' % run)
        mne.write_events(fname_events, events)
        fname_events_files.append(fname_events)

        delay = int(round(conv_freq * raw.info['sfreq']))
        events[:, 0] = events[:, 0] + delay
        events_list.append(events)

        raw_list.append(raw)

    raw, events = mne.concatenate_raws(raw_list, events_list=events_list)
    raw.set_eeg_reference(projection=True)

    raw_file = op.join(out_path, ('{}_sss_filt_ica-raw.fif'.format(subject))
    raw.save(raw_file, overwrite=True)

    event_file = op.join(out_path, '{}_sss_filt_ica-raw-eve.fif'.format(subject))
    mne.write_events(event_file, events)
    del raw_list
    del raw

    return raw_file, event_file, fname_events_files


# from 05-group_average

def compute_morph_stc(subject_id, conditions, data_path, subjects_dir):
    subject = "sub%03d" % subject_id
    print("processing subject: %s" % subject)
    out_path = op.join(data_path, subject, 'MEG')

    # Morph STCs
    stc_morphed_files = []
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
        stc_morphed_file = op.join(out_path, 'mne_dSPM_inverse_morph-%s' % (condition))
        stc_morphed.save(stc_morphed_file)

        stc_morphed_files.append(stc_morphed_file)

    return stc_morphed_files



###############################################################################
# defining new pipeline
###############################################################################

# full_pipeline
# workflow directory within the `base_dir`
src_reconstruction_pipeline_name = 'source_reconstruction_' + \
    inv_method + '_' + parc.replace('.', '')

main_workflow = pe.Workflow(name=src_reconstruction_pipeline_name)
main_workflow.base_dir = data_path



### params as json
params = json.load(open(os.path.join(rel_path, "params.json")))

data_type = params["data_type"]
subject_ids = params["subject_ids"]
NJOBS = params["NJOBS"]
session_ids = params["session_ids"]

conditions = params["conditions"]

#main_workflow = pe.Workflow(name=MAIN_WF_name)
#main_workflow.base_dir = subjects_dir

# infosource
infosource = create_iterator(['subject_id'], [subject_ids])

# datasource
template_path = "_session_id_*_subject_id_%s/ica/run_*_sss_filt_ica.fif"
template_args = [['subject_id']]
infields = ['subject_id']

# this is the dir where the cleaned raw data was saved
ica_dir = op.join(data_path,
                  'preprocessing_workflow',
                  'preproc_meeg_pipeline')


datasource = create_datagrabber(ica_dir, template_path, template_args,
                                infields=infields)


main_workflow.connect(infosource, 'subject_id',
                              datasource,  'subject_id')

# run_events_concatenate
concat_event = pe.Node(
    Function(input_names = ['list_ica_files', 'subject'],
             output_names = ['raw_file, event_file, fname_events_files'],
             function = run_events_concatenate)
    name = 'concat_event')


main_workflow.connect(datasource, 'raw_file',
                              concat_event, 'list_ica_files')

ain_workflow.connect(infosource, 'subject_id',
                              concat_event, 'subject_id')

concat_event.inputs.data_path = data_path

# source reconstruction
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

inv_sol_workflow = create_pipeline_source_reconstruction(
    data_path, subjects_dir, spacing=spacing, inv_method=inv_method,
    is_epoched=True, is_evoked=True, events_id=events_id, condition=condition,
    events_file=events_file, t_min=t_min, t_max=t_max,
    trans_fname=trans_fname, all_src_space=True, parc=parc)

main_workflow.connect(infosource, 'subject_id',
                      inv_sol_workflow, 'inputnode.sbj_id')
main_workflow.connect(concat_event, 'raw_file',
                      inv_sol_workflow, 'inputnode.raw')


# morph_stc
morph_stc = pe.Node(
    Function(input_names = ['subject_id', 'conditions', 'data_path', 'subjects_dir'],
             output_names = ['stc_morphed_files'],
             function = compute_morph_stc))


main_workflow.connect(infosource, 'subject_id',
                      morph_stc, 'subject_id')

morph_stc.inputs.conditions = conditions
morph_stc.inputs.data_path = data_path
morph_stc.inputs.subjects_dir = subjects_dir

















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
