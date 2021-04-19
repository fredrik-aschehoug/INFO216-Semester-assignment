# KG-Enricher
![GitHub](https://img.shields.io/github/license/fredrik-aschehoug/KG-Enricher)
![CI to Docker Hub](https://github.com/fredrik-aschehoug/KG-Enricher/workflows/CI%20to%20Docker%20Hub/badge.svg)
![Docker Image Version (latest by date)](https://img.shields.io/docker/v/aschehoug/kg-enricher)
![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/aschehoug/kg-enricher)
### Docker Pull Command
`docker pull aschehoug/kg-enricher`


# Build and run docker image
NOTE: replace text in \<braces\>
## Build the docker image
Navigate to the root of the repository and run:

`docker build -t <image name> .`

## Run the docker image
`docker run -p 80:80 <environment variables> <image name>`

The image expects the following environment variables:
| Variable                      | Explanation                  | Example Value                    |
| ----------------------------- | ---------------------------- | -------------------------------- |
| yago_endpoint                 | Yago4 SPARQL endpoint | https://yago-knowledge.org/sparql/query |
| yago_endpoint_max_connections | Maximum number of concurrent requests to the Yago4 endpoint | 10 |
| wd_endpoint                   | Wikidata SPARQL endpoint| https://query.wikidata.org/sparql |
| wd_endpoint_max_connections   | Maximum number of concurrent requests to the Wikidata endpoint  | 5 |

The environment variables can be supplied as arguments or with a file.

### Docker run example with aruments
`docker run -p 80:80 --env yago_endpoint=https://yago-knowledge.org/sparql/query --env yago_endpoint_max_connections=10 --env wd_endpoint=https://query.wikidata.org/sparql --env wd_endpoint_max_connections=5 <image name>`

### Docker run example with env file
`docker run -p 80:80 --env-file .\example.env <image name>`
