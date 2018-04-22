"""Utility functions.

:class EntryList: Various CLI tools relevant to displaying valid query entries.

"""

from dataset import valid_entries


class EntryList:

    """Command-line tools that assist with identifying valid entries.

    These tools do things like:

    - List all valid entries in sorted order, by different sorting key.

    - Allow the user to index into available 'query-able' entries without
      having to explicitly type them out, therefore enabling faster query
      construction.

    Full usability is described in the documentation.

    """

    def __init__(self):
        self.keys = valid_entries.keys()
        self.key_list = [key for key in self.keys]

    def sort(self, sort_key):
        """Sort valid entries.

        :param sort_key: Specifies how to sort entries.
        :type sort_key: str
        :return: Sorted entries.
        :rtype: dict

        All entries follow this syntax:
        '#year #make #model'

        To sort entries by make, split is called on each entry via lambda
        function, resulting in:

        s = ['#year', '#make', '#model]

        Therefore, a slice on 's' removing index 0 is the sort key.

        The returned dict 'result' passes the sorted entries as values to
        keys in range(0, len(entries)).  This allows the CLI entry indexing
        utility described in the class docstring.

        """
        result = {}
        if sort_key == 'year':
            self.key_list.sort()
        elif sort_key == 'make':
            self.key_list.sort(key=lambda s: s.split()[1:])

        for index, entry_key in enumerate(self.key_list):
            result[index] = entry_key
        return result
