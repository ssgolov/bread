#!/bin/bash
# Поднимает версию кэша в sw.js — иначе установленное приложение останется
# на старой сборке. Публикуется корень репозитория, поэтому сборки как таковой нет.
# Запуск:  ./build.sh      (из папки проекта)
set -e
cd "$(dirname "$0")"

V=$(date +%s | cut -c1-10)
if sed --version >/dev/null 2>&1; then
  sed -i "s/const VERSION = \"bread-v[0-9a-z]*\"/const VERSION = \"bread-v${V}\"/" sw.js
else
  sed -i '' "s/const VERSION = \"bread-v[0-9a-z]*\"/const VERSION = \"bread-v${V}\"/" sw.js
fi

grep -n 'const VERSION' sw.js
echo "готово: закоммитьте и запушьте"
