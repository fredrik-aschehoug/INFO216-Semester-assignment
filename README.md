# KG-Enricher
![GitHub](https://img.shields.io/github/license/fredrik-aschehoug/KG-Enricher)
![CI to Docker Hub](https://github.com/fredrik-aschehoug/KG-Enricher/workflows/CI%20to%20Docker%20Hub/badge.svg)
![Docker Image Version (latest by date)](https://img.shields.io/docker/v/aschehoug/kg-enricher)
![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/aschehoug/kg-enricher)
### Docker Pull Command
`docker pull aschehoug/kg-enricher`


### Docker run example
`docker run -p 80:80 --env yago_endpoint=https://yago-knowledge.org/sparql/query --env yago_endpoint_max_connections=100 --env wd_endpoint=https://query.wikidata.org/sparql --env wd_endpoint_max_connections=5 fastapi`
