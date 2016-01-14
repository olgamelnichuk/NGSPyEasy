#!/usr/bin/env bash

set -e

cd "$( dirname "${BASH_SOURCE[0]}" )"

DEST=/opt/ngspyeasy

mkdir -p ${DEST}
cp -R ./ngspyeasy/* ${DEST}

echo "##!/usr/bin/env bash
python ${DEST}/ngspyeasy.py \"\$@\"" > /usr/bin/ngspyeasy
chmod a+x /usr/bin/ngspyeasy

echo "#!/usr/bin/env bash
python ${DEST}/ngspyeasy_play_run.py \"\$@\"" > /usr/bin/ngspyeasy_play_run
chmod a+x /usr/bin/ngspyeasy_tool