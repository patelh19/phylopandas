import pandas
import dendropy

def _write_doc_template(schema):
    s = """Write to {} format.

    Parameters
    ----------
    filename : str
        File to write {} string to. If no filename is given, a {} string
        will be returned.

    taxon_col : str (default='sequence')
        Sequence column name in DataFrame.

    node_col : str (default='id')
        ID column name in DataFrame

    branch_lengths : bool (default=False)
        If True, use only the ID column to label sequences in fasta.
    """.format(schema, schema, schema)
    return s


def _pandas_df_to_dendropy_tree(
    df,
    taxon_col='uid',
    node_col='uid',
    branch_lengths=True,
    ):
    """Turn a phylopandas dataframe into a dendropy tree.

    Parameters
    ----------
    df : DataFrame
        DataFrame containing tree data.

    taxon_col : str (optional)
        Column in dataframe to label the taxon. If None, the index will be used.

    node_col : str (optional)
        Column in dataframe to label the nodes. If None, the index will be used.

    branch_lengths : bool
        If True, inclues branch lengths.
    """
    # Construct a list of nodes from dataframe.
    taxon_namespace = dendropy.TaxonNamespace()
    nodes = {}
    for idx in df.index:
        # Get node data.
        data = df.loc[idx]

        # Get taxon for node (if leaf node).
        taxon = None
        if data['type'] == 'leaf':
            taxon = dendropy.Taxon(label=data[taxon_col])
            taxon_namespace.add_taxon(taxon)

        # Get label for node.
        label = data[node_col]

        # Get edge length.
        edge_length = None
        if branch_lengths is True:
            edge_length = data['length']

        # Build a node
        n = dendropy.Node(
            taxon=taxon,
            label=label,
            edge_length=edge_length
        )

        nodes[idx] = n

    # Build branching pattern for nodes.
    root = None
    for idx, node in nodes.items():
        # Get node data.
        data = df.loc[idx]

        # Get children nodes
        children_idx = df[df['parent'] == data['id']].index
        children_nodes = [nodes[i] for i in children_idx]

        # Set child nodes
        nodes[idx].set_child_nodes(children_nodes)

        # Check if this is root.
        if data['parent'] is None:
            root = nodes[idx]

    # Build tree.
    tree = dendropy.Tree(
        seed_node=root,
        taxon_namespace=taxon_namespace
    )
    return tree


def _write(
    df,
    filename=None,
    schema='newick',
    taxon_col='uid',
    node_col='uid',
    branch_lengths=True,
    **kwargs
    ):
    """Write a phylopandas tree DataFrame to various formats.

    Parameters
    ----------
    df : DataFrame
        DataFrame containing tree data.

    filename : str
        filepath to write out tree. If None, will return string.

    schema : str
        tree format to write out.

    taxon_col : str (optional)
        Column in dataframe to label the taxon. If None, the index will be used.

    node_col : str (optional)
        Column in dataframe to label the nodes. If None, the index will be used.

    branch_lengths : bool
        If True, inclues branch lengths.
    """
    tree = _pandas_df_to_dendropy_tree(
        df,
        taxon_col=taxon_col,
        node_col=node_col,
        branch_lengths=branch_lengths,
    )

    # Write out format
    if filename is not None:
        tree.write(path=filename, schema=schema, **kwargs)
    else:
        return tree.as_string(schema=schema)


def _write_method(schema):
    """Add a write method for named schema to a class.
    """
    def method(
        self,
        filename=None,
        schema='newick',
        taxon_col='uid',
        node_col='uid',
        branch_lengths=True,
        **kwargs):
        # Use generic write class to write data.
        return _write(
            self._data,
            filename=filename,
            schema=schema,
            taxon_col=taxon_col,
            node_col=node_col,
            branch_lengths=branch_lengths,
            **kwargs
        )
    # Update docs
    method.__doc__ = _write_doc_template(schema)
    return method


def _write_function(schema):
    """Add a write method for named schema to a class.
    """
    def func(
        data,
        filename=None,
        schema='newick',
        taxon_col='uid',
        node_col='uid',
        branch_lengths=True,
        **kwargs):
        # Use generic write class to write data.
        return _write(
            data,
            filename=filename,
            schema=schema,
            taxon_col=taxon_col,
            node_col=node_col,
            branch_lengths=branch_lengths,
            **kwargs
        )
    # Update docs
    func.__doc__ = _write_doc_template(schema)
    return func


to_newick = _write_function('newick')
