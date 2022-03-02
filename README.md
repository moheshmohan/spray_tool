# spray_tool

A simple multi-threaded password spray tool written in python and packed as container. As of now it can work on web applications with form based login and ntlm based login.

Detailed explanation to configure and use the tool is provided in my blog here - [H4hacks blog post](https://www.h4hacks.com/2022/03/multithreaded-password-spray-tool.html)

## Building the docker container

The tool can be packed as a container for easy deployments. The image can be built with below command

```
docker build --tag moheshmohan/spray_tool:latest .
```

If you don't want to build the image on your own, you can pull the latest one from dockerhub. Please note this is pushed using github actions so its automated and expect some stability issues. You can pull the latest image with the below command

```
docker pull moheshmohan/spray_tool
```


## Running the tool

The tool can be run against multiple targets with each defined in a configuration file. A sample config file is already included on the repo to target [demo.testfire.net](http://demo.testfire.net/login.jsp). Sample user names and passwords are also included. The below command can be used to run on the included configuration (config.ini)

```
docker run --rm -v $(pwd):/app --name spray.conta moheshmohan/spray_tool:latest -c config.ini
```

More detailed explanation on usage will be posted soon in a blog here - [H4hacks blog post](https://www.h4hacks.com/2022/03/multithreaded-password-spray-tool.html)
