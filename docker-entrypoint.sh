#!/bin/bash
# Executing the provided command as app user
set -x
gosu app "$@"
set +x
