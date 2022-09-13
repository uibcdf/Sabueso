def get_atoms_with_alternate_locations(filename):

    from sabueso.forms.api_file_pdb import to_sabueso_PDBAtomicCoordinateEntry

    tmp_item = to_sabueso_PDBAtomicCoordinateEntry(filename)

    output = tmp_item.get_atoms_with_alternate_locations()

    for key in output:
        for ii in range(len(output[key])):
            output[key][ii]=output[key][ii].to_string(output='long_string')

    return output

