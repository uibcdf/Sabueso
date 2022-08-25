
def to_file_fasta(item, check_form=True):

    tmp_item = item.split(':')[-1]

    url = 'https://www.rcsb.org/pdb/download/downloadFastaFiles.do?structureIdList='+tmp_item+'&compressionType=uncompressed'
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    fasta_txt = response.read().decode('utf-8')

    with open(output_filename,'w') as f:
        f.write(fasta_txt)

    f.close()

    tmp_item = output_filename

    return tmp_item


