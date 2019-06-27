# reportjira

reportjira is Dockerized reportjira image, 



xhost +local:docker

aN example of docker-compose:
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
usernameJira: 'myemailJira'
tokenJira: 'mytoken' #(https://id.atlassian.com/manage/api-tokens) 
domainJira: 'domain.atlassian.net'
logo: 'logo.png'
data:
- row0:
- daily:
- 'TASK-67'
- 'daily.png'
- meeting:
- 'TASK-62'
- 'team.png'
- sys_admin:
- 'SIS-76'
- 'sysadmin.png'
- row1:
- sprint_planning:
- 'TASK-64'
- 'sprint_planning_1.png'
- retro:
- 'TASK-63'
- 'retro.png'
- grooming:
- 'TASK-68'
- 'grooming.png'
- demo:
- 'TASK-36'
- 'demo_live_1.png'
- ButtonNoId:
- ''
- 'button.jpg'
- ButtonNoIdNoImage:
```
