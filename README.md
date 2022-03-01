# spray_tool

A simple multi-threaded password spray tool written in python and packed as container. As of now it can work on web applications with form based login and ntlm based login.

## Building the docker container

The tool can be packed as a container for easy deployments. The image can be built with below command

'''
docker build --tag moheshmohan/spray_tool:latest .
'''


## Running the tool

The tool can be run against multiple targets with each defined in a configuration file. A sample config file is already included on the repo to target [demo.testfire.net](http://demo.testfire.net/login.jsp). Sample user names and passwords are also included 

More detailed explanation on usage will be posted soon in a blog. Watch this space for the link.
