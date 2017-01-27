#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
$DIR/install.sh
$DIR/before_script.sh
$DIR/script.sh
$DIR/after_script.sh
