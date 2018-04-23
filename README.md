# Access Query
A user-friendly search API enabling quick lookups of tuning data on 
COBB Tuning's [Dyno Database](https://www.cobbtuning.com/dyno-database/).

## User Interface

####`DataRange(<entry>)`:
>Retrieve min/max data for given entry.

####`MinData(<entry>)`:
>Retrieve only minimum data for given entry.

####`MaxData(<entry>)`:
>Retrieve only maximum data for given entry.

####`Comparison(<entry1>, <entry2>, ['HP', 'Torque', 'AFR', 'Boost'])`:
>Retrieve compared data for two given entries. One, any, or all listed
performance attributes may be included.

####`.search()`:
>Execute query.


## Command-line Tools
Although the package as a whole is intended for use within an application,
several command-line tools are included to assist with functional
familiarization of the package as a whole.

`YEAR` and `MAKE` are CLI utilities that allow the user to access available
'query-able' entries in various ways without having to explicitly type them
out. There are many entries, and the user is not expected to know them all,
if any.

The user can choose to:
```
display_entries_by(YEAR)
display_entries_by(MAKE)
```
These commands return dict items, where the key is within
range(0, len(entries)), with a valid lookup entry as its value.
So rather than constructing a query with an explicit entry, the user can use
the following syntax:
```
DataRange(MAKE[40]).search()
Comparison(MAKE[145], YEAR[65], ['HP', 'Boost']).search()
```
etc.

####Make some queries:
Import requred classes.
`>>> from query import *`

Queries can be made with this syntax:
```
>>> query = DataRange(YEAR[145])
>>> query.search()
>>> [MinHP(HP=111.0, RPM=2040.0), MaxHP(HP=514.0, RPM=6650.0), 
	 MinTorque(Torque=288.0, RPM=2040.0), MaxTorque(Torque=544.0, RPM=3620.0), 
	 MinAFR(AFR=11.2, RPM=5300.0), MaxAFR(AFR=14.5, RPM=2040.0), 
	 MinBoost(Boost=3.7, RPM=2040.0), MaxBoost(Boost=17.0, RPM=3220.0)]

>>> Comparison(YEAR[145], MAKE[33], ['HP', 'Torque']),search()
>>> ['HP: 2010 Nissan GT-R', 'Torque: 2010 Nissan GT-R']
```
