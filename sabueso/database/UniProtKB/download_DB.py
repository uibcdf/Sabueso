from ftplib import FTP
from datetime import datetime

def download_DB(data='reviewed', format='xml', output_filename=None, check_size=False):

    ftp_directory=None
    ftp_filename=None

    if data=='reviewed':
        ftp_directory='/pub/databases/uniprot/current_release/knowledgebase/complete/'
        if format=='xml':
            ftp_filename='uniprot_sprot.xml.gz'
        elif format=='fasta':
            ftp_filename='uniprot_sprot.fasta.gz'
        elif format=='text':
            ftp_filename='uniprot_sprot.dat.gz'
        else:
            raise ValueError('Unknown value for the input argument "format".')

    elif data=='unreviewed':
        ftp_directory='/pub/databases/uniprot/current_release/knowledgebase/complete/'
        if format=='xml':
            ftp_filename='uniprot_trembl.xml.gz'
        elif format=='fasta':
            ftp_filename='uniprot_trembl.fasta.gz'
        elif format=='text':
            ftp_filename='uniprot_trembl.dat.gz'
        else:
            raise ValueError('Unknown value for the input argument "format".')

    elif data=='isoform sequences':
        ftp_directory='/pub/databases/uniprot/current_release/knowledgebase/complete/'
        if format=='fasta':
            ftp_filename='uniprot_sprot_varsplic.fasta.gz'
        else:
            raise ValueError('The data "isoform sequences" can only be downloaded as a fasta file.')

    elif data=='uniref100':
        ftp_directory='/pub/databases/uniprot/current_release/uniref/uniref100/'
        if format=='xml':
            ftp_filename='uniref100.xml.gz'
        if format=='fasta':
            ftp_filename='uniref100.fasta.gz'
        else:
            raise ValueError('The data "uniref100" can only be downloaded as a fasta or an xml file.')

    elif data=='uniref90':
        ftp_directory='/pub/databases/uniprot/current_release/uniref/uniref100/'
        if format=='xml':
            ftp_filename='uniref90.xml.gz'
        if format=='fasta':
            ftp_filename='uniref90.fasta.gz'
        else:
            raise ValueError('The data "uniref90" can only be downloaded as a fasta or an xml file.')


    elif data=='uniref50':
        ftp_directory='/pub/databases/uniprot/current_release/uniref/uniref100/'
        if format=='xml':
            ftp_filename='uniref50.xml.gz'
        if format=='fasta':
            ftp_filename='uniref50.fasta.gz'
        else:
            raise ValueError('The data "uniref50" can only be downloaded as a fasta or an xml file.')


    else:
        raise ValueError('Unknown value for the input argument "data"')



    ftp = FTP('ftp.uniprot.org')
    ftp.login('anonymous','')
    ftp.cwd(ftp_directory)
    if check_size:
        size = ftp.size(ftp_filename)
        size = size/1048576
        ftp.close()
        return size
    else:
        if output_filename is None:
            output_filename='./'+ftp_filename
        start = datetime.now()
        ftp.retrbinary("RETR "+ftp_filename ,open(output_filename, 'wb').write)
        end = datetime.now()
        diff = end -start
        ftp.close()
        print(f'{ftp_filename} downloaded as {output_filename} in {diff}')
        pass


