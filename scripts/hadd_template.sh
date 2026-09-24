hadd -f -j 2 signal_Combined.root \
    VBF_Combined_BFull_SNottH.root \
    ggH_Combined_BFull_SNottH.root &

hadd -f -j 4 background_Combined.root \
    DY_Combined_BFull_SNottH.root \
    EWK_Combined_BFull_SNottH.root \
    DiBoson_Combined_BFull_SNottH.root \
    TT_Combined_BFull_SNottH.root &

wait

cp -f Data_Combined_BFull_SNottH.root data_Combined.root