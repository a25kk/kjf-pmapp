
Introduction
===============================

This repository holds the configuration and site packages for the kjf press release application.

Development Profile
-------------------

To initialize the development framework run

    python bootstrap.py -c development.cfg
    bin/buildout -c development.cfg

This will

 - install Plone 4.1.2
 - Run the `pressapp.policy` default profile and its dependencies
 - Setup a Plone site called **pressapp**
