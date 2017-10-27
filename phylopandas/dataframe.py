import os
import re 

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Blast import NCBIXML

import pandas as pd

def _read(filename, schema, seq_label='sequence', **kwargs):
    """Use BioPython's sequence parsing module to convert any file format to 
    a Pandas DataFrame.
    """
    # Prepare DataFrame fields.
    data = {'id':[], seq_label:[], 'description':[], 'name':[], 'db_id':[]}
    
    # Parse Fasta file.
    for i, s in enumerate(SeqIO.parse(filename, format=schema, **kwargs)):
        data['db_id'].append(s.id)
        data[seq_label].append(str(s.seq))
        data['description'].append(s.description)
        data['name'].append(s.name)
        data['id'].append('XX{:08d}'.format(i))
    
    # Port to DataFrame.
    return DataFrame(data)

def _write(dataframe, filename=None, schema='fasta', sequence_col='sequence', id_only=False, **kwargs):
    """Write a PhyloPandas DataFrame to a sequence file.
    """
    seq_records = []
    # Iterate through dataframe rows
    for i, row in dataframe.iterrows():
        seq = Seq(row[sequence_col])
        # Create a SeqRecord and append to list.
        if id_only:
            record = SeqRecord(seq, id=row['id'], name='', description='')
        else:
            record = SeqRecord(seq, id=row['id'], name=row['name'], description=row['description'])
        seq_records.append(record)
            
    # Write to disk or return string
    if filename != None:  
        SeqIO.write(seq_records, filename, format=format, **kwargs)
    else:
        return "".join([s.format(schema) for s in seq_records])

def read_fasta(filename, **kwargs):
    """Read fasta format."""
    return _read(filename, schema='fasta', **kwargs)

def read_phylip(filename, **kwargs):
    """Read phylip format."""
    return _read(filename, schema='phylip', **kwargs)

def read_clustal(filename, **kwargs):
    """Read clustal format."""
    return _read(filename, schema='clustal', **kwargs)

def read_embl(filename, **kwargs):
    """Read the EMBL flat file format."""
    return _read(filename, schema='embl', **kwargs)

def read_nexus(filename, **kwargs):
    """Read the EMBL flat file format."""
    return _read(filename, schema='nexus', **kwargs)

def read_swiss(filename, **kwargs):
    """Read Swiss-Prot aka UniProt format."""
    return _read(filename, schema='nexus', **kwargs)

def read_blast_xml(filename, **kwargs):
    """Read BLAST XML format."""
    # Read file.
    with open(filename, 'r') as f:
        blast_record = NCBIXML.read(f)    

    # Prepare DataFrame fields.
    data = {'id':[], 
        'accession':[], 
        'hit_def':[], 
        'hit_id':[], 
        'title':[],
        'length':[],
        'e_value':[],
        'sequence':[]}
    
    # Get alignments from blast result.
    for i, s in enumerate(blast_record.alignments):
        data['accession'] = s.accession
        data['hit_def'] = s.hit_def
        data['hit_id'] = s.hit_id
        data['title'] = s.title
        data['length'] = s.length
        data['e_value'] = s.hsps[0].expect
        data['sequence'] = s.hsps[0].sbjct
        
        data['id'].append('XX{:08d}'.format(i))
        
    # Port to DataFrame.
    return DataFrame(data)    


class DataFrame(pd.DataFrame):
    
    def to_fasta(self, filename=None, sequence_col='sequence', id_only=True):
        """Write to fasta format."""
        return _write(self, filename=filename, schema="fasta", id_only=True)
        
    def to_phylip(self, filename=None, sequence_col='sequence'):
        """Write to phylip format."""
        return _write(self, filename=filename, schema="phylip")

    def to_clustal(self, filename=None, sequence_col='sequence'):
        """Write to alignment format of Clustal X and Clustal W."""
        return _write(self, filename=filename, schema="clustal")
        
    def to_embl(self, filename=None, sequence_col='sequence'):
        """Write to the EMBL flat file format."""
        return _write(self, filename=filename, schema="embl")

    def to_nexus(self, filename=None, sequence_col='sequence'):
        """Write to the NEXUS multiple alignment format."""
        return _write(self, filename=filename, schema="nexus")
        
    def to_swiss(self, filename=None, sequence_col='sequence'):
        """Write Swiss-Prot aka UniProt format."""
        return _write(self, filename=filename, schema="swiss")
