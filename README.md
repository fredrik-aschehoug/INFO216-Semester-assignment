# INFO216-Semester-assignment
![GitHub](https://img.shields.io/github/license/fredrik-aschehoug/INFO216-Semester-assignment)
![CI to Docker Hub](https://github.com/fredrik-aschehoug/INFO216-Semester-assignment/workflows/CI%20to%20Docker%20Hub/badge.svg)
![Docker Image Version (latest by date)](https://img.shields.io/docker/v/aschehoug/info216-semester-assignment)
![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/aschehoug/info216-semester-assignment)
### Docker Pull Command
`docker pull aschehoug/info216-semester-assignment`


### Docker run example
`docker run -p 80:80 --env yago_endpoint=https://yago-knowledge.org/sparql/query --env yago_endpoint_max_connections=100 --env wd_endpoint=https://query.wikidata.org/sparql --env wd_endpoint_max_connections=5 fastapi`
