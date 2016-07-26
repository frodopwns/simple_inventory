Fabric Commands
===============

Right now all of the commands are in \_\_init\_\_.py.  If you want to organize your fabric commands into their own files simply create a category.py file where you want to store certain tasks then import them in the \_\_init\_\_.py file.  
This allows code in the inventory to inport from fabfile rather than fabfile.somecategory.
