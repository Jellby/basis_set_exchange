'''
Main interface to BSE functionality
'''

import os
import json
import codecs
from collections import OrderedDict
from .. import io
from .. import compose


def create_metadata_file(output_path, data_dir):

    basis_filelist = io.get_basis_filelist(data_dir)

    metadata = {}
    for bs_file_path in basis_filelist:
        filename = os.path.split(bs_file_path)[1]

        # Fully compose the basis set from components
        bs = compose.compose_table_basis(bs_file_path)

        # Prepare the metadata
        displayname = bs['basisSetName']
        defined_elements = sorted(list(bs['basisSetElements'].keys()))
        description = bs['basisSetDescription']
        revision_desc = bs['basisSetRevisionDescription']

        function_types = set()
        for e in bs['basisSetElements'].values():
            for s in e['elementElectronShells']:
                function_types.add(s['shellFunctionType'])
            if 'elementECP' in e:
                function_types.add('ECP')

        function_types = sorted(list(function_types))

        # convert the file path to the internal identifier for the basis set
        internal_name = os.path.basename(bs_file_path)
        internal_name = internal_name.replace(".table.json", "")

        # split out the version number
        internal_name, ver = os.path.splitext(internal_name)
        ver = int(ver[1:])

        single_meta = OrderedDict([('filename', filename), ('description', description), ('revdesc', revision_desc),
                                   ('functiontypes', function_types), ('elements', defined_elements)])

        if not displayname in metadata:
            metadata[displayname] = {'versions': {ver: single_meta}}
        else:
            metadata[displayname]['versions'][ver] = single_meta

    # sort the versions and find the max version
    for k, v in metadata.items():
        metadata[k] = OrderedDict([('latest_version', max(v['versions'].keys())),
                                   ('versions', OrderedDict(sorted(v['versions'].items())))])

    # Write out the metadata
    metadata = OrderedDict(sorted(list(metadata.items())))
    with codecs.open(output_path, 'w', 'utf-8') as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
