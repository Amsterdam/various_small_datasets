#!/bin/bash
set -e

if [ "$1" = 'mapproxy' ]; then
  echo "Running additional provisioning"
  for f in /docker-entrypoint-initmapproxy.d/*; do
    case "$f" in
      */*.sh)     echo "$0: running $f"; . "$f" ;;
      */mapproxy.yml)   cp /docker-entrypoint-initmapproxy.d/mapproxy.yml /mapproxy/mapproxy.yaml ;;
      */mapproxy.yaml) cp /docker-entrypoint-initmapproxy.d/mapproxy.yaml /mapproxy/mapproxy.yaml ;;
    esac
    echo
  done

  server_list=($(echo $MAPSERVERS | tr ";" "\n"))
  echo $server_list
  for server in ${server_list}; do
    echo "Creating config for $server"
    project_name=`echo $server | awk -F[/:] '{print $4}'`
    mapproxy-util autoconfig \
      --capabilities="$server" \
      --overwrite /mapproxy/overwrite.yaml \
      --output /mapproxy/${project_name}.yaml \
      --force
  done

  echo "Start mapproxy"
  # --wsgi-disable-file-wrapper is required because of https://github.com/unbit/uwsgi/issues/1126
  if [ "$2" = 'http' ]; then
    exec uwsgi --wsgi-disable-file-wrapper --http 0.0.0.0:8080 --wsgi-file /mapproxy/app.py --master --enable-threads --processes $MAPPROXY_PROCESSES --threads $MAPPROXY_THREADS --stats 0.0.0.0:9191
    exit
  fi

  exec uwsgi --wsgi-disable-file-wrapper --http-socket 0.0.0.0:8080 --wsgi-file /mapproxy/app.py --master --enable-threads --processes $MAPPROXY_PROCESSES --threads $MAPPROXY_THREADS --stats 0.0.0.0:9191
  exit
fi

exec "$@"
