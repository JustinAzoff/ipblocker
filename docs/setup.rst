=======
Setup
=======

Add ipblocker user
------------------
.. code-block:: bash

    root# adduser --disabled-password ipblocker

Install dependencies
--------------------
.. code-block:: bash

    root# apt-get install python-{setuptools,virtualenv,psycopg2,httplib2,simplejson,paramiko,geoip} postgresql-8.3 timeout

Create database
---------------

Create the ipblocker database, and ipblocker username and password.  You will
need to add this password to the configuration file later on.

.. code-block:: bash

    root@ su - postgres
    postgres$ createuser -S -D -R  -P ipblocker
    Enter password for new role:
    Enter it again:
    postgres$ createdb -O ipblocker ipblocker
    postgres$ exit

Install IPBlocker
-----------------
.. code-block:: bash

    root# su - ipblocker
    ipblocker$ virtualenv ipblocker_env
    ipblocker$ . ipblocker_env/bin/activate
    (ipblocker_env)ipblocker$ easy_install -f http://www.albany.edu/~ja6447/ipblocker/ ipblocker snort pynfdump

Set up Router Access
--------------------
To access the router using the cisco library you'll need to create a
~/.cisco/credentials file.  This file should contain three tab delimited
columns consisting of the router username, the password, and the enable
password.  If any of these values are not needed they should be set to 'None'

.. code-block:: bash

    ipblocker$ mkdir ~/.cisco
    ipblocker$ touch ~/.cisco/credentials
    ipblocker$ chmod 600 ~/.cisco/credentials
    ipblocker$ editor ~/.cisco/credentials
    #add tab deliminated
    username        password        enablepassword

Example:

.. code-block:: bash

    None    cisco   cisco

Make the initial ipblocker cfg file
-----------------------------------
Using the example.cfg_

.. _example.cfg: example.cfg

You will need to change the following:

* The database password that you set in the "Create database" step.
* The database hostname if the database is running on a separate machine.
* The nullrouter IP address

.. code-block:: bash

    ipblocker$ cp docs/example.cfg ~/ipblocker.cfg #or /etc/ipblocker/ipblocker.cfg
    ipblocker$ chmod 600 ipblocker.cfg
    ipblocker$ editor ipblocker.cfg

Test Router Access
------------------

This ensures that the cisco library is installed properly and that the
credential file is correct.

::

    (ipblocker_env)ipblocker@ipblocker:~$ ipblocker-cli test_cisco_router_access
    Attempting to login to 192.168.1.1
    2010-10-29 11:34:27,498 - paramiko.transport - INFO - Connected (version 2.0, client Cisco-1.25)
    2010-10-29 11:34:27,998 - paramiko.transport - INFO - Authentication (password) successful!
    2010-10-29 11:34:28,002 - paramiko.transport - INFO - Secsh channel 1 opened.
    Login Successful
    Currently null-routing 1538 addresses

Create the database tables
--------------------------

This creates the empty IPBlocker database tables.

.. code-block:: python

    (ipblocker_env)ipblocker$ python
    >>> from ipblocker import model
    >>> model.metadata.create_all()
    >>> [Control-d]

Test database
-------------
.. code-block:: bash

    (ipblocker_env)ipblocker$ ipblocker-list-blocked

(no output expected)

Block stuff
-----------

Block ZuesTracker block list
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: bash

    (ipblocker_env)ipblocker$ ipblocker-block-zeustracker

    2010-09-02 17:30:35,652 - ipblocker - DEBUG - Fetching IP list from the zeus tracker
    2010-09-02 17:30:36,707 - ipblocker - DEBUG - removed 89 US ips
    2010-09-02 17:30:36,719 - ipblocker - DEBUG - Got 338 ips
    2010-09-02 17:30:37,327 - ipblocker - DEBUG - DB-blocking 109.104.92.192
    2010-09-02 17:30:37,498 - ipblocker - DEBUG - DB-blocking 109.196.130.43
    ...

Implement the blocks
~~~~~~~~~~~~~~~~~~~~
.. code-block:: bash

    (ipblocker_env)ipblocker$ ipblocker-manage-nullroutes

    2010-09-02 17:35:58,641 - ipblocker - DEBUG - Logging into router
    2010-09-02 17:35:58,912 - ipblocker - DEBUG - Done logging into router
    2010-09-02 17:36:01,586 - ipblocker - INFO - blocking 109.104.92.192 (zeus)
    2010-09-02 17:36:01,586 - ipblocker - INFO - blocking 109.196.130.43 (zeus)
    ...
    2010-09-02 17:36:28,020 - ipblocker - DEBUG - Logging out of router

Test CLI
--------
.. code-block:: bash

    (ipblocker_env)ipblocker$ ipblocker-cli show 109.104.92.192
    109.104.92.192  | State: blocked | zeus | 2010-09-02

    #or

    (ipblocker_env)ipblocker$ ipblocker-cli
    IPBlocker> show 109.104.92.192
    109.104.92.192  | State: blocked | zeus | 2010-09-02
    IPBlocker> [Control-d]



Set up Crontab
--------------
::

    PATH=/bin:/usr/bin:/home/ipblocker/ipblocker_env/bin
    # m h  dom mon dow   command
    * * * * * timeout 200 ipblocker-manage-nullroutes
    0 * * * * sleep 20;timeout 600 ipblocker-block-zeustracker > /dev/null
    #* * * * * sleep 45;timeout 100 ipblocker-block-snort > /dev/null
