#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <tuples_version>"
    echo "Example: $0 2.2.0"
    exit 1
fi

TUPLES_VERSION="$1"

# Require format a.b.c where a, b, and c are integers
if [[ ! "$TUPLES_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: tuples_version must be of the form a.b.c (e.g. 2.2.0)"
    exit 1
fi

SOURCE_DIR="/store/group/lpchmumu/mbarrial/analyzer_HiggsMuMu_v2.2/tuples_v${TUPLES_VERSION}/haddTuples/"

echo "Copying tuples version v${TUPLES_VERSION}"
echo "Source: ${SOURCE_DIR}"

xrdfs root://cmseos.fnal.gov ls "$SOURCE_DIR" \
| grep '\.root$' \
| while read -r file; do
    xrdcp "root://cmseos.fnal.gov/$file" .
done