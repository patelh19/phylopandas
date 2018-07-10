# Import pandas
import pandas as pd
from pandas_flavor import register_dataframe_accessor, register_series_accessor

from functools import wraps

from . import seqio
from . import treeio


@register_series_accessor('phylo')
class PhyloPandasSeriesMethods(object):
    """
    """
    def __init__(self, data):
        self._data = data

    # -----------------------------------------------------------
    # Extra write methods.
    # -----------------------------------------------------------

    to_fasta = seqio.write._write_method('fasta')
    to_phylip = seqio.write._write_method('phylip')
    to_clustal = seqio.write._write_method('clustal')
    to_embl = seqio.write._write_method('embl')
    to_nexus = seqio.write._write_method('nexus')
    to_swiss = seqio.write._write_method('swiss')
    to_fastq = seqio.write._write_method('fastq')
    to_fasta_twoline = seqio.write._write_method('fasta-2line')


@register_dataframe_accessor('phylo')
class PhyloPandasDataFrameMethods(object):
    """PhyloPandas accessor to the Pandas DataFrame.

    This accessor adds reading/writing methods to the pandas DataFrame that
    are specific to phylogenetic data.
    """
    def __init__(self, data):
        self._data = data

    # -----------------------------------------------------------
    # Extra read methods.
    # -----------------------------------------------------------

    # Sequence file reading methods
    read_fasta = seqio.read._read_method('fasta')
    read_phylip = seqio.read._read_method('phylip')
    read_clustal = seqio.read._read_method('clustal')
    read_embl = seqio.read._read_method('embl')
    read_nexus = seqio.read._read_method('nexus')
    read_swiss = seqio.read._read_method('swiss')
    read_fastq = seqio.read._read_method('fastq')
    read_fasta_twoline = seqio.read._read_method('fasta-2line')

    # Tree file reading methods.
    read_newick = treeio.read._read_method('newick')

    # -----------------------------------------------------------
    # Extra write methods.
    # -----------------------------------------------------------

    to_fasta = seqio.write._write_method('fasta')
    to_phylip = seqio.write._write_method('phylip')
    to_clustal = seqio.write._write_method('clustal')
    to_embl = seqio.write._write_method('embl')
    to_nexus = seqio.write._write_method('nexus')
    to_swiss = seqio.write._write_method('swiss')
    to_fastq = seqio.write._write_method('fastq')
    to_fasta_twoline = seqio.write._write_method('fasta-2line')

    # -----------------------------------------------------------
    # Useful dataframe methods specific to sequencing data.
    # -----------------------------------------------------------

    def match_value(self, column, value):
        """Return a subset dataframe that column values match the given value.

        Parameters
        ----------
        column : string
            column to search for matches

        value : float, int, list, etc.
            values to match.
        """
        # Get column
        col = self._data[column]

        # Get items in a list
        try:
            idx = col[col.isin(value)].index

        # Or value is a single item?
        except TypeError:
            idx = col[col == value].index

        return self._data.loc[idx]


    def combine(self, other, on='index'):
        """Combine two dataframes. Update the first dataframe with second.
        New columns are added after the dataframe. Overlapping columns update
        the values of the columns.

        Technical note: maintains order of columns, appending new dataframe to
        old.

        Parameters
        ----------
        other : DataFrame
            Index+Columns that match self will be updated with new values.
            New rows will be added separately.

        on : str
            Column to update index.
        """
        # # Determine column labels for new dataframe (Maintain order of columns)
        # column_idx = {k: None for k in self._data.columns}
        # column_idx.update({k: None for k in other.columns})
        # column_idx = list(column_labels.keys())

        df0 = self._data
        df1 = other

        # Save index as column in df
        df0['index'] = df0.index
        df1['index'] = df1.index

        # Set index to whatever column is given
        df0.set_index(on, inplace=True, drop=False)
        df1.set_index(on, inplace=True, drop=False)

        # Write out both dataframes to dictionaries
        data0 = df0.to_dict(orient="index")
        data1 = df1.to_dict(orient="index")

        for key in data1.keys():
            try:
                data0[key].update(data1[key])
            except KeyError:
                data0[key] = data1[key]

        # Build new dataframe
        df = pd.DataFrame(data0).T

        # Reset index
        df.set_index('index', inplace=True, drop=True)
        df.index.name = None

        # Store dataframe
        self._data = df
        return self._data

        #
        #
        # df0.index = idx
        #
        #
        #
        #
        #
        #
        # df0 = self._data.to_dict()
        # df1 = other.to_dict()
        #
        #
        #
        #
        #
        #
        #
        #
        #
        # # If index is passed, update on index
        # if on == 'index':
        #     self._data = self._data.combine_first(other)
        #
        # elif on in self._data.columns:
        #
        #     # Move index of current dataframe
        #     df0 = self._data
        #     df0['index'] = df0.index
        #     df0.set_index(on, inplace=True)
        #
        #     # Reset index of new dataframe
        #     df1 = other
        #     df1.set_index(on, inplace=True)
        #
        #     # Update
        #     from IPython.display import display
        #     display(df1)
        #
        #     df0.combine_first(df1)
        #     display(df0)
        #
        #     # Change index back to uid.
        #     df0['id'] = df0.index
        #     df0.set_index('index', inplace=True)
        #     df0.index.name = None # Remove name of index
        #
        #     # Store data (with old order).
        #     print(df0.columns)
        #     self._data = df0[list(column_labels.keys())]

        return self._data
