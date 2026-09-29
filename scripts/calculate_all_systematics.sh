#!/bin/bash

set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 2.2.1"
    exit 1
fi

VERSION=$1

python3 scripts/print_systematics_eff.py
python3 scripts/print_systematics_pileup.py
python3 scripts/print_systematics_pt.py "$VERSION"
