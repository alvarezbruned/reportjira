# reportjira

reportjira is Dockerized reportjira image, 


xhost +local:docker

An example of docker-compose:
```
version: '2'
services:
  reportjira:
    image: 'albertalvarezbruned/reportjira'
    container_name: 'reportjira'
    volumes:
      - '/tmp/.X11-unix:/tmp/.X11-unix'
      - './your-path-of-settings/data-work.yaml:/root/data-work.yaml'
      - '/Users/robert/Documents/images/:/Users/robert/Documents/images/'
    environment:
      - 'DISPLAY=:0'

```

An example of 'data-work.yaml':

```
pathImages: '/Users/robert/Documents/images/'
pixelsIcon : '60'
usernameJira: 'myemailJira'
tokenJira: 'mytoken' #(https://id.atlassian.com/manage/api-tokens)
domainJira: 'domain.atlassian.net'
pathToLog: '/path/mi.log'
logo: 'logo.png'
data:
  - row0:
    - incidencias:
      - 'TASK-11006'
      - 'mierda1.png'
    - infojobs:
      - 'TASK-11006'
      - 'infojolps 1.png'
    - daily:
      - 'TASK-43'
      - 'daily_1.png'
    - reunion:
      - 'TASK-46'
      - 'team.png'
    - sys_admin:
      - 'TASK-1173'
      - 'sysadmin_1.png'
    - descanso:
      - ''
      - 'burger_refresh.png'
    - bash_start:
      - 'CMD ONLY'
      - 'logo-start.png'
      - 'echo "start" > /files/sem/ACTION && rm /files/sem/stop-sel'
    - ButtonNoIdNoImage:
  - row1:
    - retro:
      - 'TASK-41'
      - 'retro_1.png'
    - grooming:
      - 'TASK-44'
      - 'grooming_1.png'
    - demo:
      - 'TASK-42'
      - 'demo_live_1.png'
```
