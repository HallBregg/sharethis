# Sharethis Local Deploy
### Quickstart
Local deploy is used to imitate production environment.

We have NGINX configured to listen on two domains:
`api.localhost`
`bucket.localhost`
You can add those domains to `/etc/hosts` on your machine.
```shell
cat /etc/hosts

## Sharethis config
127.0.0.1	localhost api.localhost bucket.localhost
###
```


To simply start whole project execute:
```shell
docker-compose up
```
*** Wait for db is in development so in case of an error while starting,
execute Ctrl+C and execute this command one more time.

All services should now be available. NGINX listens on port 80.
