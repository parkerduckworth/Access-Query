"""The module defines the querying interface for the user.

BASE CLASS
:class Query: Base class for all querying.

USER INTERFACE
:class DataRange: Retrieve min/max data for given entry.
:class MinData: Retrieve min data for given entry
:class MaxData: Retrieve max data for given entry
:class Comparison: Retrieve compared data for two given entries

Although the package as a whole is intended for use within an application,
several command-line tools are included to assist with functional
familiarization of the package as a whole.

'YEAR' and 'MAKE' are CLI utilities that allow the user to access available
'query-able' entries in various ways without having to explicitly type them
out. There are many entries, and the user is not expected to know them all,
if any.

The user can choose to:
display_entries_by(YEAR)
display_entries_by(MAKE)

These commands return dict items, where the key is within
range(0, len(entries)), with a valid lookup entry as its value.

So rather than constructing a query with an explicit entry, the user can use
the following syntax:

DataRange(MAKE[40]).search()
Comparison(MAKE[145], YEAR[65], ['HP', 'Boost']).search()
etc.

A detailed explanation of the user interface, constructing queries, and using
the CLI tools is provided in the documentation.

"""

from collections import namedtuple
from content import DataParser
from utils import EntryList


# Dicts containing entries sorted according to provided argument.
YEAR = EntryList().sort('year')
MAKE = EntryList().sort('make')


def display_entries_by(key_map):
    """Pretty print a dict."""
    for items in key_map.items():
        print(items)


class Query(DataParser):

    """Retrieving and distributing data processed by the DataParser class.

    Query is a generalized class that serves processed content to its
    various user interface subclasses, which build the result and return the
    user's query.

    """

    def __init__(self, entry):
        DataParser.__init__(self, entry)

    def generate_result(self, value=None):
        """Retrieve and distribute requested data.

        :param value: Optional parameter that allows a subclass to make a more
                      specific data request. None by default.
        :type value: str if specified, otherwise None.
        :return: requested data
        :rtype: dict

        """
        data, result = self.get_data_range(), {}
        if value == 'min':

            # Retrieve only minimum values
            for key in data.keys():
                result[key] = data[key]['min']
        elif value == 'max':

            # Retrieve only minimum values
            for key in data.keys():
                result[key] = data[key]['max']
        else:

            # Retrieve all values
            result = data

        return result


class DataRange(Query):

    """Min and max values of a query's available performance attributes."""

    def __init__(self, entry):
        Query.__init__(self, entry)

    def build_result(self, data):
        """Usefully structure query data in a user-readable form.

        :param data: Data payload received from base class.
        :type data: dict
        :return: Minimum and maximum values for queried entry.
        :rtype: list[namedtuple]

        The 'data' dict's access syntax in the min/max payloads is explained
        in detail in the DataParser().initialize_data_range_container()
        docstring in the 'content.py' module.

        """
        result = []
        for i in range(len(self.perf_attrs)):
            # Collect and traverse performance attributes.
            attr = self.perf_attrs[i]

            # Instantiate namedtuple to house minimum data.
            min = namedtuple('Min{}'.format(attr), [attr, 'RPM'])

            # Instantiate namedtuple to house maximum data.
            max = namedtuple('Max{}'.format(attr), [attr, 'RPM'])

            # Populate minimum data and assign to payload.
            min_payload = min(data[attr]['min'][0], data[attr]['min'][1])

            # Populate minimum data and assign to payload.
            max_payload = max(data[attr]['max'][0], data[attr]['max'][1])

            result.append(min_payload)
            result.append(max_payload)

        return result

    def search(self):
        """Initiate query.

        :return: Requested data.
        :rtype: list[namedtuple]

        """
        return self.build_result(self.generate_result())


class MinData(DataRange):

    """Minimum value queries.

    Subclassing DataRange enables a simple filtering for minimum values.
    Minimum values will always populate on even indices, and can be accessed
    using the slice notation in this class' search() method.

    """

    def __init__(self, entry):
        DataRange.__init__(self, entry)

    def search(self):
        """Initiate query for minimum values.

        :return: Requested data.
        :rtype: list[namedtuple]

        """
        return self.build_result(self.generate_result())[::2]


class MaxData(DataRange):

    """Maximum value queries.

    Operates exactly like its sibling class MinData, with the exception that
    maximum values populate on odd-numbered indices, as reflected in the slice
    within this class' search method.

    """

    def __init__(self, entry):
        DataRange.__init__(self, entry)

    def search(self):
        """Initiate query for maximum values.

        :return: Requested data.
        :rtype: list[namedtuple]
        """
        return self.build_result(self.generate_result())[1::2]


class Comparison(Query):

    """Queries that compare two entries' attributes.


    Due to the binary nature of comparisons, it is only necessary for this
    class to compare entries' maximum values.

    """

    def __init__(self, entry, other, attr_list):
        """Construct a comparison query.

        :param other: Second entry to be compared to the first.
        :type other: str
        :param attr_list: Attributes to compare.
        :type attr_list: list[str]

        """
        Query.__init__(self, entry)
        self._other = other
        self._attr_list = attr_list

        # First entry's attribute values.
        self._lhs_operand = self.generate_result('max')

        # Second entry's attribute values.
        self._rhs_operand = Query(self._other).generate_result('max')

    def build_result(self, entry, other):
        """Usefully structure query data in a user-readable form.

        :param entry: First entry's attribute values.
        :type entry: dict
        :param other: Second entry's attribute values.
        :type other: dict
        :return: Requested data.
        :rtype: list[str]

        """

        result = []
        for attr in self._attr_list:

            # Not all entries have every attribute recorded.
            try:

                # Entry syntax -> 'Entry'[# attr_data, # RPM_data], so index zero is accessed.
                first_operand, second_operand = entry[attr][0],  other[attr][0]

                if first_operand > second_operand:
                    result.append(attr + ': ' + self._entry)
                elif second_operand > first_operand:
                    result.append(attr + ': ' + self._other)
                else:
                    result.append(attr + ': Equal')

            # If one or both entries are missing an attribute.
            except KeyError:
                result.append(('{} data not available for this comparison.'.format(attr)))

        return result

    def search(self):
        """Initiate query.

        :return: Requested data
        :rtype: list[str]

        """
        return self.build_result(self._lhs_operand, self._rhs_operand)
