# KG-Enricher
![GitHub](https://img.shields.io/github/license/fredrik-aschehoug/KG-Enricher)
![CI to Docker Hub](https://github.com/fredrik-aschehoug/KG-Enricher/workflows/CI%20to%20Docker%20Hub/badge.svg)
![Docker Image Version (latest by date)](https://img.shields.io/docker/v/aschehoug/kg-enricher)
![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/aschehoug/kg-enricher)
### Docker Pull Command
```
docker pull aschehoug/kg-enricher
```


# Build and run Docker image
> NOTE: replace text in \<braces\>
## Build the Docker image
Navigate to the root of the repository and run:

```
docker build -t <image name> .
```

## Run the Docker image
```
docker run -p 80:80 <environment variables> <image name>
```

The image expects the following environment variables:
| Variable                      | Explanation                                                    | Example Value                           |
| ----------------------------- | -------------------------------------------------------------- | --------------------------------------- |
| yago_endpoint                 | Yago4 SPARQL endpoint                                          | https://yago-knowledge.org/sparql/query |
| yago_endpoint_max_connections | Maximum number of concurrent requests to the Yago4 endpoint    | 10                                      |
| wd_endpoint                   | Wikidata SPARQL endpoint                                       | https://query.wikidata.org/sparql       |
| wd_endpoint_max_connections   | Maximum number of concurrent requests to the Wikidata endpoint | 5                                       |

The environment variables can be supplied as arguments or with a file.

### Docker run example with aruments
```
docker run -p 80:80 --env yago_endpoint=https://yago-knowledge.org/sparql/query --env yago_endpoint_max_connections=10 --env wd_endpoint=https://query.wikidata.org/sparql --env wd_endpoint_max_connections=5 <image name>
```

### Docker run example with env file
```
docker run -p 80:80 --env-file .\example.env <image name>
```

# Run application outside Docker
Navigate to the root of the repository before proceeding.
## (Optional) Create a virtual environment for the application
Create the environment:

```
py -m venv env
```

Then activate it:

```
.\env\Scripts\activate
```

## Install dependencies
```
pip install -r dev-requirements.txt
```

## Run from command line
You can [set the environment variables in your shell](https://fastapi.tiangolo.com/advanced/settings/?h=environment#environment-variables)
or use a file like in the Docker example.

First navigate to the app directory:

```
cd app
```

Then run uvicorn to start the app:

```
uvicorn main:app --reload --port 8000
```

You can also provide an env file for the environment variables:
```
uvicorn main:app --reload --port 8000 --env-file <path to env file>
```

## Debug in VS Code
It is also possible to debug the app in VS Code. This makes it possible to set breakpoints, etc.
But keep in mind that it has a major performance impact.

All you need to do is to [create a launch configuration](https://code.visualstudio.com/docs/editor/debugging#_launch-configurations)
for the project and add the following configuration to it:
```json
{
    "name": "Python: FastAPI",
    "type": "python",
    "request": "launch",
    "module": "uvicorn",
    "args": [
        "main:app",
        "--reload",
        "--port",
        "8000"
    ],
    "env": {
        "yago_endpoint": "https://yago-knowledge.org/sparql/query",
        "yago_endpoint_max_connections": "5",
        "wd_endpoint": "https://query.wikidata.org/sparql",
        "wd_endpoint_max_connections": "5",
    },
    "console": "integratedTerminal",
    "cwd": "${workspaceFolder}/app"
}
```

You can of course customnize the properties in "env" to your liking.