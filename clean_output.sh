#!/usr/bin/env bash

repo_root=$(git rev-parse --show-toplevel)
pushd $repo_root > /dev/null
rm -rf ./output/*
popd > /dev/null
