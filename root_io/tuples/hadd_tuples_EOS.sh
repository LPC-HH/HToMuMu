#!/bin/bash

ANALYZER_VERSION="v2.4"
TUPLES_VERSION="v2.4.2"

EOS_PATH="/eos/uscms/store/group/lpchmumu/$USER/analyzer_HiggsMuMu_$ANALYZER_VERSION/tuples_$TUPLES_VERSION/"
inEOS_PATH="/store/group/lpchmumu/$USER/analyzer_HiggsMuMu_$ANALYZER_VERSION/tuples_$TUPLES_VERSION/"

COPY_TO_EOS=false
DELETE_AFTER_COPY=false


############################################################
# Parse options
############################################################

while [[ $# -gt 0 ]]; do

    case "$1" in

        -c)
            COPY_TO_EOS=true
            DELETE_AFTER_COPY=false
            ;;

        -eos)
            COPY_TO_EOS=true
            DELETE_AFTER_COPY=true
            ;;

        *)
            echo "[ERROR] Unknown option: $1"
            echo
            echo "Usage:"
            echo "  $0          # hadd locally and keep local files"
            echo "  $0 -c       # hadd locally, copy to EOS, keep local files"
            echo "  $0 -eos     # hadd locally, copy to EOS, delete local files"
            exit 1
            ;;

    esac

    shift

done


############################################################
# Prepare EOS directory
############################################################

if $COPY_TO_EOS; then

    echo
    echo "============================================================"

    if $DELETE_AFTER_COPY; then
        echo " EOS MODE"
        echo " hadd locally -> copy to EOS -> delete local file"
    else
        echo " COPY MODE"
        echo " hadd locally -> copy to EOS -> keep local file"
    fi

    echo "============================================================"
    echo "EOS destination:"
    echo "${inEOS_PATH}haddTuples/"
    echo "============================================================"
    echo

    eosmkdir "${inEOS_PATH}haddTuples/" 2>/dev/null || true

else

    echo
    echo "============================================================"
    echo " LOCAL MODE"
    echo " hadd locally -> keep local file"
    echo "============================================================"
    echo

fi


COPY_MAX_RETRIES=10
COPY_RETRY_DELAY=10


merge()
{
    OUTPUT_FILE="$1"
    shift

    echo
    echo "============================================================"
    echo "Creating: ${OUTPUT_FILE}"
    echo "============================================================"


    hadd -f "${OUTPUT_FILE}" "$@"

    HADD_STATUS=$?

    if [ $HADD_STATUS -ne 0 ]; then
        echo
        echo "[ERROR] hadd failed for:"
        echo "        ${OUTPUT_FILE}"
        echo
        return 1
    fi

    if $COPY_TO_EOS; then
        
        EOS_OUTPUT="root://cmseos.fnal.gov//${inEOS_PATH#/}haddTuples/${OUTPUT_FILE}"

        echo
        echo "Copying ${OUTPUT_FILE} to EOS..."
        echo "Destination:"
        echo "    ${EOS_OUTPUT}"
        echo

        COPY_SUCCESS=false

        for ATTEMPT in $(seq 1 ${COPY_MAX_RETRIES}); do

            echo "------------------------------------------------------------"
            echo "EOS copy attempt ${ATTEMPT}/${COPY_MAX_RETRIES}"
            echo "------------------------------------------------------------"

            eos cp "${OUTPUT_FILE}" "${EOS_OUTPUT}"

            COPY_STATUS=$?

            if [ $COPY_STATUS -eq 0 ]; then

                COPY_SUCCESS=true

                echo
                echo "[OK] EOS copy successful on attempt ${ATTEMPT}"
                echo

                break

            fi


            echo
            echo "[WARNING] EOS copy attempt ${ATTEMPT} failed."

            if [ $ATTEMPT -lt $COPY_MAX_RETRIES ]; then
                echo "Retrying in ${COPY_RETRY_DELAY} seconds..."
                echo
                sleep ${COPY_RETRY_DELAY}
            fi

        done


        if ! $COPY_SUCCESS; then

            echo
            echo "============================================================"
            echo "[ERROR] EOS COPY FAILED"
            echo "============================================================"
            echo "File:"
            echo "    ${OUTPUT_FILE}"
            echo
            echo "Failed after ${COPY_MAX_RETRIES} attempts."
            echo
            echo "Local file will be kept."
            echo "============================================================"
            echo

            return 1

        fi


        if $DELETE_AFTER_COPY; then

            echo "Removing local file:"
            echo "    ${OUTPUT_FILE}"

            rm -f "${OUTPUT_FILE}"

        else

            echo "Keeping local file:"
            echo "    ${OUTPUT_FILE}"

        fi

    fi

    return 0
}



############################################################
# 2022
############################################################

echo
echo "############################################################"
echo "# 2022"
echo "############################################################"

merge Data_2022_tuples.root \
    ${EOS_PATH}Muon_2022{C..D}/*.root \
    ${EOS_PATH}SingleMuon_2022C/*.root

merge DY_2022_tuples.root \
    ${EOS_PATH}DY50to120_Summer22/*.root \
    ${EOS_PATH}DY120to200_Summer22/*.root

merge EWK_2022_tuples.root \
    ${EOS_PATH}EWK_2L2J_Summer22/*.root

merge TT_2022_tuples.root \
    ${EOS_PATH}TTto2L2Nu_Summer22/*.root \
    ${EOS_PATH}TTtoLNu2Q_Summer22/*.root

merge DiBoson_2022_tuples.root \
    ${EOS_PATH}WZto2L2Q_*22/*.root \
    ${EOS_PATH}WZto3LNu_*22/*.root \
    ${EOS_PATH}ZZto2L2Nu_*22/*.root \
    ${EOS_PATH}ZZto2L2Q_*22/*.root \
    ${EOS_PATH}ZZto4L_*22/*.root \
    ${EOS_PATH}WWto2L2Nu_*22/*.root

merge ggH_2022_tuples.root \
    ${EOS_PATH}ggH_*22/*.root

merge VBF_2022_tuples.root \
    ${EOS_PATH}VBF_*22/*.root

merge ttH_2022_tuples.root \
    ${EOS_PATH}ttH_*22/*.root



############################################################
# 2022EE
############################################################

echo
echo "############################################################"
echo "# 2022EE"
echo "############################################################"

merge Data_2022EE_tuples.root \
    ${EOS_PATH}Muon*_2022{E..G}/*.root

merge DY_2022EE_tuples.root \
    ${EOS_PATH}DY50to120_Summer22EE/*.root \
    ${EOS_PATH}DY120to200_Summer22EE/*.root

merge EWK_2022EE_tuples.root \
    ${EOS_PATH}EWK_2L2J_Summer22EE/*.root

merge TT_2022EE_tuples.root \
    ${EOS_PATH}TTto2L2Nu_Summer22EE/*.root \
    ${EOS_PATH}TTtoLNu2Q_Summer22EE/*.root

merge DiBoson_2022EE_tuples.root \
    ${EOS_PATH}WZto2L2Q_*22EE/*.root \
    ${EOS_PATH}WZto3LNu_*22EE/*.root \
    ${EOS_PATH}ZZto2L2Nu_*22EE/*.root \
    ${EOS_PATH}ZZto2L2Q_*22EE/*.root \
    ${EOS_PATH}ZZto4L_*22EE/*.root \
    ${EOS_PATH}WWto2L2Nu_*22EE/*.root

merge ggH_2022EE_tuples.root \
    ${EOS_PATH}ggH_*22EE/*.root

merge VBF_2022EE_tuples.root \
    ${EOS_PATH}VBF_*22EE/*.root

merge ttH_2022EE_tuples.root \
    ${EOS_PATH}ttH_*22EE/*.root



############################################################
# 2023
############################################################

echo
echo "############################################################"
echo "# 2023"
echo "############################################################"

merge Data_2023_tuples.root \
    ${EOS_PATH}Muon*_2023C*/*.root

merge DY_2023_tuples.root \
    ${EOS_PATH}DY50to120_Summer23/*.root \
    ${EOS_PATH}DY120to200_Summer23/*.root

merge EWK_2023_tuples.root \
    ${EOS_PATH}EWK_2L2J_Summer23/*.root

merge TT_2023_tuples.root \
    ${EOS_PATH}TTto2L2Nu_Summer23/*.root \
    ${EOS_PATH}TTtoLNu2Q_Summer23/*.root

merge DiBoson_2023_tuples.root \
    ${EOS_PATH}WZto2L2Q_*23/*.root \
    ${EOS_PATH}WZto3LNu_*23/*.root \
    ${EOS_PATH}ZZto2L2Nu_*23/*.root \
    ${EOS_PATH}ZZto2L2Q_*23/*.root \
    ${EOS_PATH}ZZto4L_*23/*.root \
    ${EOS_PATH}WWto2L2Nu_*23/*.root

merge ggH_2023_tuples.root \
    ${EOS_PATH}ggH_*23/*.root

merge VBF_2023_tuples.root \
    ${EOS_PATH}VBF_*23/*.root

merge ttH_2023_tuples.root \
    ${EOS_PATH}ttH_*23/*.root



echo
echo "############################################################"
echo "# 2023BPix"
echo "############################################################"

merge Data_2023BPix_tuples.root \
    ${EOS_PATH}Muon*_2023D*/*.root

merge DY_2023BPix_tuples.root \
    ${EOS_PATH}DY50to120_Summer23BPix/*.root \
    ${EOS_PATH}DY120to200_Summer23BPix/*.root

merge EWK_2023BPix_tuples.root \
    ${EOS_PATH}EWK_2L2J_Summer23BPix/*.root

merge TT_2023BPix_tuples.root \
    ${EOS_PATH}TTto2L2Nu_Summer23BPix/*.root \
    ${EOS_PATH}TTtoLNu2Q_Summer23BPix/*.root

merge DiBoson_2023BPix_tuples.root \
    ${EOS_PATH}WZto2L2Q_*23BPix/*.root \
    ${EOS_PATH}WZto3LNu_*23BPix/*.root \
    ${EOS_PATH}ZZto2L2Nu_*23BPix/*.root \
    ${EOS_PATH}ZZto2L2Q_*23BPix/*.root \
    ${EOS_PATH}ZZto4L_*23BPix/*.root \
    ${EOS_PATH}WWto2L2Nu_*23BPix/*.root

merge ggH_2023BPix_tuples.root \
    ${EOS_PATH}ggH_*23BPix/*.root

merge VBF_2023BPix_tuples.root \
    ${EOS_PATH}VBF_*23BPix/*.root

merge ttH_2023BPix_tuples.root \
    ${EOS_PATH}ttH_*23BPix/*.root


echo
echo "############################################################"
echo "# 2024"
echo "############################################################"

merge Data_2024_tuples.root \
    ${EOS_PATH}Muon*_2024*/*.root

merge DY_2024_tuples.root \
    ${EOS_PATH}DY50to120_Summer24/*.root \
    ${EOS_PATH}DY120to200_Summer24/*.root

merge EWK_2024_tuples.root \
    ${EOS_PATH}EWK_2L2J_Summer24/*.root

merge TT_2024_tuples.root \
    ${EOS_PATH}TTto2L2Nu_Summer24/*.root \
    ${EOS_PATH}TTtoLNu2Q_Summer24/*.root

merge DiBoson_2024_tuples.root \
    ${EOS_PATH}WZto2L2Q_*24/*.root \
    ${EOS_PATH}WZto3LNu_*24/*.root \
    ${EOS_PATH}ZZto2L2Nu_*24/*.root \
    ${EOS_PATH}ZZto2L2Q_*24/*.root \
    ${EOS_PATH}ZZto4L_*24/*.root \
    ${EOS_PATH}WWto2L2Nu_*24/*.root

merge ggH_2024_tuples.root \
    ${EOS_PATH}ggH_*24/*.root

merge VBF_2024_tuples.root \
    ${EOS_PATH}VBF_*24/*.root

merge ttH_2024_tuples.root \
    ${EOS_PATH}ttH_*24/*.root



############################################################
# 2025
############################################################

echo
echo "############################################################"
echo "# 2025"
echo "############################################################"

merge Data_2025_tuples.root \
    ${EOS_PATH}Muon*_2025*/*.root

merge DY_2025_tuples.root \
    ${EOS_PATH}DY50to120_Summer25/*.root \
    ${EOS_PATH}DY120to200_Summer25/*.root

merge EWK_2025_tuples.root \
    ${EOS_PATH}EWK_2L2J_Summer25/*.root

merge TT_2025_tuples.root \
    ${EOS_PATH}TTto2L2Nu_Summer25/*.root \
    ${EOS_PATH}TTtoLNu2Q_Summer25/*.root

merge DiBoson_2025_tuples.root \
    ${EOS_PATH}WZto2L2Q_*25/*.root \
    ${EOS_PATH}WZto3LNu_*25/*.root \
    ${EOS_PATH}ZZto2L2Nu_*25/*.root \
    ${EOS_PATH}ZZto2L2Q_*25/*.root \
    ${EOS_PATH}ZZto4L_*25/*.root \
    ${EOS_PATH}WWto2L2Nu_*25/*.root

merge ggH_2025_tuples.root \
    ${EOS_PATH}ggH_*25/*.root

merge VBF_2025_tuples.root \
    ${EOS_PATH}VBF_*25/*.root

############################################################
# 2026
############################################################

echo
echo "############################################################"
echo "# 2026"
echo "############################################################"

merge Data_2026_tuples.root \
    ${EOS_PATH}Muon*_2026*/*.root

############################################################
# Finished
############################################################

echo
echo "============================================================"
echo " ALL HADD JOBS FINISHED"
echo "============================================================"

if $COPY_TO_EOS; then

    echo "Files were copied to:"
    echo "${inEOS_PATH}haddTuples/"

    if $DELETE_AFTER_COPY; then
        echo "Local copies were deleted after successful EOS copies."
    else
        echo "Local copies were kept."
    fi

else

    echo "Files were stored locally only."

fi

echo "============================================================"
