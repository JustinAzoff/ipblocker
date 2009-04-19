=======
Setup
=======

Add ipblocker user
------------------
.. code-block:: bash

    root# adduser --disabled-password ipblocker

Install everything
------------------
.. code-block:: bash

    root# apt-get install python-setuptools python-virtualenv python-psycopg2 postgresql-8.3
    root# su - ipblocker
    ipblocker$ virtualenv ipblocker_env
    ipblocker$ . ipblocker_env/bin/activate
    (ipblocker_env)ipblocker$ easy_install cisco*gz cymruwhois*gz ieeemac*gz\
                pynfdump*gz snort*gz ren_isac*gz ipblocker*gz python-memcached



Setup cisco library
-------------------
::

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
    >>> from cisco.ciscolib import login
    >>> c = login("router_ip")
    >>> c is not None
    True
    >>> print c.nullroute_list()
    [list of current nullrouted IPS]


Make the initial ipblocker cfg file
-----------------------------------
.. code-block:: bash

    ipblocker$ cp docs/example.cfg ~/ipblocker.cfg #or /etc/ipblocker/ipblocker.cfg
    ipblocker$ chmod 600 ipblocker.cfg
    ipblocker$ vim ipblocker.cfg #edit database and other passwords

Create database
---------------
.. code-block:: bash

    root@ su - postgres
    postgres$ createuser -S -D -R  -P ipblocker
    postgres$ createdb -O ipblocker ipblocker

Create the tables
~~~~~~~~~~~~~~~~~
::

    ipblocker$ python
    >>> from ipblocker import model
    >>> model.metadata.create_all()

Test database
-------------
.. code-block:: bash

    (ipblocker_env)ipblocker$ ipblocker-list-blocked

(no output expected)

Block stuff
-----------

Block ren-isac list
~~~~~~~~~~~~~~~~~~~
.. code-block:: bash

    (ipblocker_env)ipblocker$ ipblocker-block-ren-isac 
    2009-01-29 14:38:00,368 - ipblocker - DEBUG - Fetching IP list from ren-isac
    2009-01-29 14:38:01,402 - ipblocker - DEBUG - Got 453 ips
    2009-01-29 14:38:01,435 - ipblocker - DEBUG - DB-blocking 11.22.33.44
    2009-01-29 14:38:01,447 - ipblocker - DEBUG - DB-blocking 55.66.77.88
    ...

Implement the blocks
~~~~~~~~~~~~~~~~~~~~
.. code-block:: bash

    (ipblocker_env)ipblocker$ ipblocker-manage-nullroutes
    2009-01-29 14:41:21,940 - ipblocker - DEBUG - Logging into router
    2009-01-29 14:41:22,172 - ipblocker - DEBUG - Done logging into router
    2009-01-29 14:41:22,230 - ipblocker - INFO - blocking 11.22.33.44 (ren-isac)
    2009-01-29 14:41:22,230 - ipblocker - INFO - blocking 55.66.77.88 (ren-isac)
    ...
    2009-01-29 14:42:00,187 - ipblocker - DEBUG - Logging out of router



Setup Crontab
-------------
::

    PATH=$PATH:~/ipblocker_env/bin
    # m h  dom mon dow   command
    * * * * * timeout 200 ipblocker-manage-nullroutes
    0 * * * * sleep 20;timeout 600 ipblocker-block-ren-isac > /dev/null
    #* * * * * sleep 45;timeout 100 ipblocker-block-snort > /dev/null
