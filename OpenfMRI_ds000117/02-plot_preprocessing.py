"""
===================
Preprocess MEG data
===================
The preprocessing pipeline runs the ICA algorithm for an
automatic removal of eyes and heart related artefacts.
A report is automatically generated and can be used to correct
and/or fine-tune the correction in each subject.
"""

# Authors: Annalisa Pascarella <a.pascarella@iac.cnr.it>
#          Mainak Jas <mainakjas@gmail.com>
# License: BSD (3-clause)

import nipype.pipeline.engine as pe

from params import data_path, data_type, subject_ids, session_ids, NJOBS
from ephypype.nodes import create_iterator, create_datagrabber


###############################################################################
# Read the parameters for preprocessing from a json file and print it
import json  # noqa
import pprint  # noqa
data = json.load(open("params_preprocessing.json"))
pprint.pprint({'preprocessing parameters': data})

l_freq = data['l_freq']
h_freq = data['h_freq']
ECG_ch_name = data['ECG_ch_name']
EoG_ch_name = data['EoG_ch_name']
variance = data['variance']
reject = data['reject']

###############################################################################
# Then, we create our workflow and specify the `base_dir` which tells
# nipype the directory in which to store the outputs.

# workflow directory within the `base_dir`
preproc_pipeline_name = 'preprocessing_workflow'

main_workflow = pe.Workflow(name=preproc_pipeline_name)
main_workflow.base_dir = data_path

###############################################################################
# Then we create a node to pass input filenames to DataGrabber from nipype

infosource = create_iterator(['subject_id', 'session_id'],
                             [subject_ids, session_ids])

###############################################################################
# and a node to grab data. The template_args in this node iterate upon
# the values in the infosource node

template_path = '*%s/MEG/run*%s*sss.fif'
template_args = [['subject_id', 'session_id']]
datasource = create_datagrabber(data_path, template_path, template_args)

###############################################################################
# Ephypype creates for us a pipeline which can be connected to these
# nodes we created. The preprocessing pipeline is implemented by the function
# ephypype.pipelines.preproc_meeg.create_pipeline_preproc_meeg, thus to
# instantiate this pipeline node, we import it and pass our
# parameters to it.

from ephypype.pipelines.preproc_meeg import create_pipeline_preproc_meeg  # noqa
preproc_workflow = create_pipeline_preproc_meeg(
    data_path, l_freq=l_freq, h_freq=h_freq,
    variance=variance, ECG_ch_name=ECG_ch_name, EoG_ch_name=EoG_ch_name,
    data_type=data_type)

###############################################################################
# We then connect the nodes two at a time. First, we connect the two outputs
# (subject_id and session_id) of the infosource node to the datasource node.
# So, these two nodes taken together can grab data.

main_workflow.connect(infosource, 'subject_id', datasource, 'subject_id')
main_workflow.connect(infosource, 'session_id', datasource, 'session_id')

###############################################################################
# Similarly, for the inputnode of the preproc_workflow. Things will become
# clearer in a moment when we plot the graph of the workflow.

main_workflow.connect(infosource, 'subject_id',
                      preproc_workflow, 'inputnode.subject_id')
main_workflow.connect(datasource, 'raw_file',
                      preproc_workflow, 'inputnode.raw_file')

###############################################################################
# To do so, we first write the workflow graph (optional)

main_workflow.write_graph(graph2use='colored')  # colored


###############################################################################
# Finally, we are now ready to execute our workflow.

main_workflow.config['execution'] = {'remove_unnecessary_outputs': 'false'}

# Run workflow locally on 1 CPU
main_workflow.run(plugin='LegacyMultiProc', plugin_args={'n_procs': NJOBS})
