#!/usr/bin/env bash

set -ex;

destination=fontawesome
base_url=https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/

brands=(
  github
);

regular=(
);

solid=(
  book
  tv
);

for icon in "${brands[@]}"; do
  icon="${icon}.svg";
  icon_path="${destination}/brands/${icon}";
  mkdir -p "$(dirname ${icon_path})";
  [ -f "${icon_path}" ] || wget -O "${icon_path}" "${base_url}/brands/${icon}";
done;

for icon in "${regular[@]}"; do
  icon="${icon}.svg";
  icon_path="${destination}/regular/${icon}";
  mkdir -p "$(dirname ${icon_path})";
  [ -f "${icon_path}" ] || wget -O "${icon_path}" "${base_url}/regular/${icon}";
done;

for icon in "${solid[@]}"; do
  icon="${icon}.svg";
  icon_path="${destination}/solid/${icon}";
  mkdir -p "$(dirname ${icon_path})";
  [ -f "${icon_path}" ] || wget -O "${icon_path}" "${base_url}/solid/${icon}";
done;
