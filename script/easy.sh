#!/usr/bin/env bash

# 完整清單
#names=( "桃園" "天祥" "苑裡" "三地門" "甲仙" "新興" "馬頭山" "三貂角" "佳里" "宜梧" "花蓮" "池上" "綠島" "潮州" "臺北" "宜蘭" "北門" "大湖" "阿里山" "玉山" )
# 數量有效清單
#names=( "桃園" "苑裡" "三地門" "甲仙" "新興" "馬頭山" "佳里" "宜梧" "潮州" )
names=( "桃園" "桃園" "桃園" "桃園" "桃園" "桃園" "桃園" "桃園" "桃園" "桃園" )
names=( "${names[@]}" "苑裡" "苑裡" "苑裡" "苑裡" "苑裡" "苑裡" "苑裡" "苑裡" "苑裡" "苑裡" )
names=( "${names[@]}" "三地門" "三地門" "三地門" "三地門" "三地門" "三地門" "三地門" "三地門" "三地門" "三地門" )
names=( "${names[@]}" "甲仙" "甲仙" "甲仙" "甲仙" "甲仙" "甲仙" "甲仙" "甲仙" "甲仙" "甲仙" )
names=( "${names[@]}" "新興" "新興" "新興" "新興" "新興" "新興" "新興" "新興" "新興" "新興" )
names=( "${names[@]}" "馬頭山" "馬頭山" "馬頭山" "馬頭山" "馬頭山" "馬頭山" "馬頭山" "馬頭山" "馬頭山" "馬頭山" )
names=( "${names[@]}" "佳里" "佳里" "佳里" "佳里" "佳里" "佳里" "佳里" "佳里" "佳里" "佳里" )
names=( "${names[@]}" "宜梧" "宜梧" "宜梧" "宜梧" "宜梧" "宜梧" "宜梧" "宜梧" "宜梧" "宜梧" )
names=( "${names[@]}" "潮州" "潮州" "潮州" "潮州" "潮州" "潮州" "潮州" "潮州" "潮州" "潮州" )

# 完整清單
#lead_times=( "20" "40" "60" "80" "100" "120" )
lead_times=( "120" )
#

# 完整清單
#selection_methods=( "split" "rotation" )
selection_methods=( "rotation" )

# 完整清單
#do_deltas=( "delta" "no_delta" )
do_deltas=( "delta" )

# 完整清單
#fields=( "0.1.2.3.4.5.6.7.8.9.10.11.12" "9.10.11.12" "0.1.2.3.4.5.6.7.8.10.11.12" "0.1.2.3.4.5.6.7.8.9.11.12" "0.1.2.3.4.5.6.7.8.9.10.12" "0.1.2.3.4.5.6.7.8.9.10.11" )
fields=( "0.1.2.3.4.5.6.7.8.9.10.11" )

for name in "${names[@]}"
do
    # 將原始資料轉換成中間檔案，單一月份資料約一小時，轉換的日期範圍在 convert.py 內
    #./convert.py "$name"

    filename=$(./global_config.py "$name")

    for lead_time in "${lead_times[@]}"
    do
        for selection_method in "${selection_methods[@]}"
        do
            for do_delta in "${do_deltas[@]}"
            do
                for field in "${fields[@]}"
                do
                    # 從中間檔案產生訓練資料，約 2 秒鐘
                    ./generate-train-data.py "$name" "$lead_time" "$selection_method" "$do_delta" "$field"

                    train_file=${filename}-${lead_time}-${selection_method}-${do_delta}-${field}-train
                    test_file=${filename}-${lead_time}-${selection_method}-${do_delta}-${field}-test

                    # 產生有效樣本數
                    #train_lines=$(wc -l < ${train_file})
                    #test_lines=$(wc -l < ${test_file})
                    #echo ${name} \& ${train_lines} \& ${train_lines} \\\\

                    #if [ "$train_lines" == "0" ] || [ "$test_lines" == "0" ]; then
                    #    echo ${name}\'s ${train_file} or its test file is empty.
                    #    continue
                    #fi

                    cd ../libsvm/tools
                    # 訓練，約一分鐘內
                    ./easy.py "../../script/$train_file" "../../script/$test_file" > /dev/null

                    cd - > /dev/null
                    # 檢視各類正確率，約半分鐘內
                    echo -n ${name}
                    ./compare.py "$train_file" "$test_file" "../libsvm/tools/$test_file.predict"
                done
            done
        done
    done
done
