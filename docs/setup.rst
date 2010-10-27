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

Setup cisco library
-------------------
.. code-block:: bash

    ipblocker$ mkdir ~/.cisco
    ipblocker$ touch ~/.cisco/credentials
    ipblocker$ chmod 600 ~/.cisco/credentials
    ipblocker$ edit ~/.cisco/credentials
    #add tab deliminated
    username        password        enablepassword

Test cisco library
------------------
::

    (ipblocker_env)ipblocker$ python
    >>> from cisco import login
    >>> c = login("router_ip")
    >>> c is not None
    True
    >>> print c.nullroute_list()
    [list of current nullrouted IPS]
    >>> [Control-d]


Make the initial ipblocker cfg file
-----------------------------------
Using the example.cfg_

.. _example.cfg: example.cfg

.. code-block:: bash

    ipblocker$ cp docs/example.cfg ~/ipblocker.cfg #or /etc/ipblocker/ipblocker.cfg
    ipblocker$ chmod 600 ipblocker.cfg
    ipblocker$ vim ipblocker.cfg #edit database and other passwords


Create the tables
-----------------
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



Setup Crontab
-------------
::

    PATH=/bin:/usr/bin:/home/ipblocker/ipblocker_env/bin
    # m h  dom mon dow   command
    * * * * * timeout 200 ipblocker-manage-nullroutes
    0 * * * * sleep 20;timeout 600 ipblocker-block-zeustracker > /dev/null
    #* * * * * sleep 45;timeout 100 ipblocker-block-snort > /dev/null
