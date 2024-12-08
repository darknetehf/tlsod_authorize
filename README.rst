===============
tlsod_authorize
===============

A small tool to authorize the provisioning of TLS on demand against an inventory of domain names.

.. contents:: Table of Contents


General principles
------------------

This is a simple HTTP endpoint written in Python. It is designed to be used along with the Caddy webserver for the automatic provisioning of SSL certificates.
See references below for more background information.

The inventory of domain names is stored in a SQLite database file. The file will be created upon first run if it does not already exist.

How it works
------------

The embedded web server expects a request in this format:

.. code-block::

   http://tlsod:8080?domain=test.com

Possible answers are as follows:

 ========================================================== =============
  description                                                status code
 ========================================================== =============
  Domain name found in inventory                             200
  Domain name not found in inventory                         404
  Invalid request or domain name missing from query string   400
  Server error                                               500
 ========================================================== ============= 

Usage
-----

Example:

.. code-block:: bash

   tlsod-authorize --port 8080  --db ~/domains.sqlite

Remarks:

- Port is optional (default: 8080)
- The DB path must be a valid file path for the file system

Importing data
--------------

At this time, there is no interface for populating the database. Since the SQLite format is easy to work with, you can either use the command line, or figure out your own interface.

Example: provided that you have a CSV file containing a list of domain names, the file could be imported from the command line like this:

.. code-block:: bash

   sqlite3 domains.sqlite
   .import /path/to/domains.csv domains

Count:

.. code-block:: sql

   SELECT COUNT(*) FROM domains;

NB: domain name lookup is not case-sensitive.

Caddy
-----

A sample Caddy file is provided to show how to use the container for TLS on demand.

Docker
------

The application was designed to be run in Docker. You can use the sample docker-compose.yml file to generate an image. It is recommended to keep the database file in a Docker volume for persistence.
The container should be joined to an existing network that is reachable by the Caddy webserver.

Limitations
-----------

- The application should handle concurrent requests but has not been tested under heavy load.
- Domain name lookup is performed in a *case-insensitive* manner. Therefore, no index is used and the queries are not optimized. However, the use of a LIMIT clause should prevent a full table scan and return as soon as a matching record is found.

References
----------

- `Serving tens of thousands of domains over HTTPS with Caddy <https://caddy.community/t/serving-tens-of-thousands-of-domains-over-https-with-caddy/11179>`_
