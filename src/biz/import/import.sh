#!/usr/bin/env bash

set -e   # stop on any error

CUR_DIR=`pwd`
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $SCRIPT_DIR
DATABASE_HOST=${DATABASE_HOST:-localhost}
DATABASE_PORT=${DATABASE_PORT:-5408}
DATABASE_NAME=${DATABASE_NAME:-various_small_datasets}
DATABASE_USER=${DATABASE_USER:-various_small_datasets}
DATABASE_PASSWORD=${DATABASE_PASSWORD:-insecure}

# Register database credentials
CREDENTIALS="${DATABASE_HOST}:${DATABASE_PORT}:${DATABASE_NAME}:${DATABASE_USER}:${DATABASE_PASSWORD}"
if ! grep -Fxq $CREDENTIALS ~/.pgpass > /dev/null; then
    echo $CREDENTIALS >> ~/.pgpass
    chmod 600 ~/.pgpass
fi

psql -h ${DATABASE_HOST} -p ${DATABASE_PORT} -U ${DATABASE_USER} ${DATABASE_NAME} -c "drop table biz_data;"
cat biz_data_create.sql| psql -h ${DATABASE_HOST} -p ${DATABASE_PORT} -U ${DATABASE_USER} ${DATABASE_NAME}
cat biz_data_insert.sql| psql -h ${DATABASE_HOST} -p ${DATABASE_PORT} -U ${DATABASE_USER} ${DATABASE_NAME}

cd $CUR_DIR
