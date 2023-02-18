#!/usr/bin/env bash
hugo;
AWS_PROFILE="s3" hugo deploy;
