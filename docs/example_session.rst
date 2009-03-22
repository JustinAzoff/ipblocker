Example Session
===============

With a fresh install, nothing will be blocked::

    justin@dell ~ % ipblocker-list
    Blocked

    Block Pending

    UnBlock Pending


Block an IP address for 60 seconds::

    justin@dell ~ % ipblocker-block 4.4.4.4 testing 60  


There will now be a single block pending::

    justin@dell ~ % ipblocker-list
    Blocked

    Block Pending
    4.4.4.4

    UnBlock Pending


Manually run the nullroute manager to block the address::

    justin@dell ~ % ipblocker-manage-nullroutes       
    2008-05-22 10:14:38,063 - ipblocker - DEBUG - Logging into router
    2008-05-22 10:14:38,291 - ipblocker - DEBUG - Done logging into router
    2008-05-22 10:14:38,356 - ipblocker - INFO - blocking 4.4.4.4
    2008-05-22 10:14:39,337 - ipblocker - DEBUG - Logging out of router


The address is now blocked::

    justin@dell ~ % ipblocker-list
    Blocked
    4.4.4.4 2008-05-22 10:15:33.810608 1 minute

    Block Pending

    UnBlock Pending


After a minute, it will be time for the address to be unblocked::

    justin@dell ~ % sleep 60
    justin@dell ~ % ipblocker-list
    Blocked
    4.4.4.4 2008-05-22 10:15:33.810608 less than a minute ago

    Block Pending

    UnBlock Pending
    4.4.4.4

Manually run the nullroute manager to unblock the address::

    justin@dell ~ % ipblocker-manage-nullroutes
    2008-05-22 10:15:39,145 - ipblocker - DEBUG - Logging into router
    2008-05-22 10:15:39,379 - ipblocker - DEBUG - Done logging into router
    2008-05-22 10:15:39,442 - ipblocker - INFO - unblocking 4.4.4.4
    2008-05-22 10:15:40,428 - ipblocker - DEBUG - Logging out of router



Error Handling
--------------

IPBlocker will not update the database unless it can confirm that an
address was blocked or unblocked.

Block a single address again for a minute::

    justin@dell ~ % ipblocker-block 4.4.4.4 testing 60
    justin@dell ~ % ipblocker-list
    Blocked

    Block Pending
    4.4.4.4

    UnBlock Pending

    justin@dell ~ % ipblocker-manage-nullroutes
    2008-05-22 10:16:31,505 - ipblocker - DEBUG - Logging into router
    2008-05-22 10:16:31,738 - ipblocker - DEBUG - Done logging into router
    2008-05-22 10:16:31,803 - ipblocker - INFO - blocking 4.4.4.4
    2008-05-22 10:16:32,785 - ipblocker - DEBUG - Logging out of router


Temporarily knock the test router off the network to simulate a problem::

    noctester2#config t
    noctester2(config)#int gig0/1
    noctester2(config-if)#shutdown 

Run the nullroute manager::

    justin@dell ~ % ipblocker-manage-nullroutes
    2008-05-22 10:17:56,024 - ipblocker - DEBUG - Logging into router
    2008-05-22 10:17:58,028 - ipblocker - ERROR - Unable to login to router
    2008-05-22 10:17:58,029 - ipblocker - ERROR - error unblocking Unable to login to router


Restore connectivity::

    noctester2#config t
    noctester2(config)#int gig0/1
    noctester2(config-if)#no shutdown 

Run the nullroute manager::

    justin@dell ~ % ipblocker-manage-nullroutes
    2008-05-22 10:19:08,692 - ipblocker - DEBUG - Logging into router
    2008-05-22 10:19:08,926 - ipblocker - DEBUG - Done logging into router
    2008-05-22 10:19:08,989 - ipblocker - INFO - unblocking 4.4.4.4
    2008-05-22 10:19:09,981 - ipblocker - DEBUG - Logging out of router
