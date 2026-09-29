if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
    echo "Usage: $0 <tuples_version> [era]"
    echo "Example: $0 2.2.0"
    echo "Example: $0 2.2.0 2023BPix"
    exit 1
fi

TUPLES_VERSION="$1"
ERA="${2:-}"

# Require format a.b.c where a, b, and c are integers
if [[ ! "$TUPLES_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: tuples_version must be of the form a.b.c (e.g. 2.2.0)"
    exit 1
fi

# Validate era if provided
if [ -n "$ERA" ]; then
    case "$ERA" in
        2022|2022EE|2023|2023BPix|2024|2025|Combined)
            ;;
        *)
            echo "Error: invalid era '$ERA'"
            echo "Allowed eras: 2022, 2022EE, 2023, 2023BPix, 2024, 2025, Combined"
            exit 1
            ;;
    esac
fi

SOURCE_DIR="/store/group/lpchmumu/mbarrial/analyzer_HiggsMuMu_v2.2/tuples_v${TUPLES_VERSION}/haddTuples/"

echo "Copying tuples version v${TUPLES_VERSION}"
echo "Source: ${SOURCE_DIR}"

if [ -n "$ERA" ]; then
    echo "Filtering files for era: ${ERA}"

    xrdfs root://cmseos.fnal.gov ls "$SOURCE_DIR" \
    | grep '\.root$' \
    | grep "${ERA}_" \
    | while read -r file; do
        xrdcp "root://cmseos.fnal.gov/$file" .
    done
else
    echo "No era specified; copying all ROOT files"

    xrdfs root://cmseos.fnal.gov ls "$SOURCE_DIR" \
    | grep '\.root$' \
    | while read -r file; do
        xrdcp "root://cmseos.fnal.gov/$file" .
    done
fi