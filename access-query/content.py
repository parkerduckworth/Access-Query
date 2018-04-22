"""Collection of classes that manage content captured in each 'API' call.

:class ContentLoader: Responsible for making the 'API' call.
:class DataParser: Usefully organizes the captured content.

"""

from collections import OrderedDict

import pandas as pd


URL = 'https://dyno.cobbtuning.com/dyno/getrundetails.php?runid1='


def urlify(url, index):
    """
    Concatenate an index to a generic url to enable multiple lookups.

    :param url: Incomplete url without an index.
    :type url: str
    :param index: Index  that completes input url.
    :type: str
    :return: Complete url.
    :rtype: str

    """
    return url + '{}'.format(index)


class ContentLoader:

    """Responsible for calling the 'API' and receiving a payload.

    API is enclosed in quotes because although it behaves like one, the call
    for content is not officially through an API.

    The identifier 'valid_entries' imported from 'dataset.py' is dict of valid
    lookup entries that serve as 'API keys', whose values hold reference to
    their respective HTML table ID.

    """

    def __init__(self, entry):
        """Construct an instance of ContentLoader.

        The ContentLoader constructor is never explicitly called. This class
        exists only to be subclassed.

        :param entry: A reference to key in 'valid_entries', enabling content
                      lookup.
        :type entry: str

        """
        self._entry = entry
        self._data = self.load_content()

    def get_content_index(self, entry):
        """Retrieve inputted entry's lookup table ID."""
        try:

            # Attempt an entry API key lookup
            from dataset import valid_entries
            index = valid_entries[entry]
        except KeyError:

            # Entry does not exist.
            raise Exception('Invalid entry.')
        return index

    def load_content(self):
        """Make 'API' call to retrieve and load content.

        :return: Requested data payload.
        :rtype: list
        """
        index = self.get_content_index(self._entry)
        url = urlify(URL, index)

        # Scrape appropriate HTML table using pandas.
        data = pd.read_html(url, header=0)

        return data


class DataParser(ContentLoader):

    """Parsing and structuring captured content for easy querying.

    Due to the lack of an official API necessitating a raw HTML scrape,
    pandas delivers content payload in the following fashion:

    data[head, body], or data[0, 1]

    This is further broken down into:

    head = {head.keys() : head.values}
    body = {body.keys() : body.values}

    Throughout this class
    data[1] ->        Again, data[body], which lists the various performance
                      attributes and their respective values, throughout each
                      vehicle's tested RPM range.
    data[1].keys() -> Refers to a list of each attribute's name.
                      ('HP', 'Torque', etc.)
    data[1].values -> Refers to a matrix of recorded values of each attribute.

    Going into why keys is a method and values is an attribute is beyond the
    scope of this docstring, and isn't pertinent to understanding any program
    functionality.

    If interested, visit:
    https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html

    """

    def __init__(self, entry):
        """Construct an instance of DataParser.

        Like its superclass, it is never explicitly called, but exists to
        provide functionality to subclasses.

        """
        ContentLoader.__init__(self, entry)

        # Data member _values is assigned to the captured data matrix.
        self._values = self._data[1].values
        self.perf_attrs = self.get_performance_attrs()
        self.data_range = self.initialize_data_range_container()

    def get_performance_attrs(self):
        """Get list of performance attributes from loaded content.

        The first attribute is RPM, which is not directly queried, hence the
        slice on keys() -> [1:]

        :returns: List of attributes available for query.
        :rtype: list

        """
        performance_attrs = self._data[1].keys()[1:]
        return performance_attrs

    def initialize_data_range_container(self):
        """Generate container to parse and organize loaded content.

        Content will be organized by performance attribute. The container is a
        dict initialized with these attributes as keys.

        Each key has a nested dict with 'min' and 'max' keys, each with a list
        initialized to length of 2. These lists house the requested attribute's
        measure and its respective RPM.

        The goal of this structure is to retain well organized data for
        efficient lookups and ease of constructing query functions.

        {
            'HP': {
                'min': [#min HP, #RPM at that HP],
                'max': [#max HP, #RPM at that HP]
                },
            'Torque': {
                'min': [#etc., #etc.],
                'max': [#etc., #etc.]
                },
            #etc.
        }

        :return: Initialized container ready to house data.
        :rtype: dict[dict[list]]

        """
        # Container keys initialized to performance attributes.
        data_container = OrderedDict.fromkeys(self.perf_attrs)
        for key in data_container.keys():

            # Container keys assigned storage for data values.
            data_container[key] = {'min': [float('inf'), float('inf')], 'max': [0, 0]}

        return data_container

    def get_data_range(self):
        """
        Return data container with requested information.

        :return: Populated data container.
        :rtype: dict[dict[list]]
        """
        data = self.data_range

        # OrderedDict keys casted to list to enable indexing.
        dict_index = list(data.keys())

        # Traverse data matrix
        for col in range(1, len(self._values[0])):
            for row in range(len(self._values)):

                # Not all entries have every attribute recorded.
                try:

                    # Compare entry value to already recorded max value in data container.
                    if self._values[row][col] > data[dict_index[col - 1]]['max'][0]:

                        # Overwrite recorded value if entry value is greater.
                        data[dict_index[col - 1]]['max'][0] = float('{0:0.1f}'.format(self._values[row][col]))

                        # Include respective RPM measure at new recorded value
                        data[dict_index[col - 1]]['max'][1] = self._values[row][0]

                    # Compare entry value to already recorded min value in data container.
                    if self._values[row][col] < data[dict_index[col - 1]]['min'][0]:

                        # Overwrite recorded value if entry value is lesser.
                        data[dict_index[col - 1]]['min'][0] = float('{0:0.1f}'.format(self._values[row][col]))

                        # Include respective RPM measure at new recorded value
                        data[dict_index[col - 1]]['min'][1] = self._values[row][0]

                # Attribute is not recorded for entry, continue traversal.
                except IndexError:
                    continue

        return data
