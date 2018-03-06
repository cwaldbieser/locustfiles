============
Locust Files
============

--------------
CAS v5  Locust
--------------

Create a file called `$PROJECT_HOME/cas5/credentials.csv`.
The fields should be:

login,password

Run the locustfile with:

.. code-block:: bash

    $ locust -f cas5/locustfile.py --host=https://cas.stage.lafayette.edu

