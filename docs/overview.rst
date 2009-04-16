Overview
========

Design
------

IPBlocker consists of a number of components 

.. image:: diagram.*

IPBlocker Database
------------------

The core of the IPBlocker service is its backend database. This database stores
a list of all the IPs that

    * Are pending being blocked
    * Are currently blocked
    * Are pending being un-blocked
    * Have been unblocked 

For each IP the following is also stored

    * The time the address was blocked
    * The time the address should be unblocked
    * The time the address was unblocked
    * The user or system who requested the block
    * The reason for the block 
    * If traffic to the address should be flagged for review

There is also a table that stores a list of networks that should never be
blocked, and a table(fishy) that lists ip addresses that should be blocked if
they set off a single alert.
