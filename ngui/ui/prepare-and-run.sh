#!/bin/sh -eu

function initializeEnvironmentVariables(){
    echo "window.optscale = window.optscale || {};";
    for i in `env | grep '^VITE'`
    do
        key=$(echo "$i" | cut -d"=" -f1);
        val=$(echo "$i" | cut -d"=" -f2);
        echo "window.optscale.${key}='${val}' ;";
    done
}

function allowAppIndexing(){
    ROBOTS_TXT_PATH=/usr/src/app/ui/public/robots.txt
    > $ROBOTS_TXT_PATH
    {
        echo "User-agent: *"
        echo "Allow: /"
    } >> $ROBOTS_TXT_PATH
}

initializeEnvironmentVariables > /usr/src/app/ui/build/config.js

# updating script include version in html file, to drop client browser cache
current_timestamp=`date +%s`
sed -i /usr/src/app/ui/build/index.html -e "s/\${buildVersion}/${current_timestamp}/" /usr/src/app/ui/build/index.html

if [ "$BUILD_MODE" = "production" ]; then
   allowAppIndexing
fi

# running application
node ./dist/server.js