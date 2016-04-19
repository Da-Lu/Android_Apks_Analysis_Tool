#!/bin/bash
clear
if [ ! -z "$2" ];then
	cd $2
fi
cd resources
cd FlowDroid
echo "Flow analysis ..."
./flowDroid.sh $1
cd ..
cd Client
echo "Decompiling apk files ..."
./decompiler.sh $1
if [ ! -z "$2" ];then
	exit;
fi
cd ..
cd Covert
echo "Extracting apk models ..."
./covert.sh model $1
echo "Merging apk models ..."
./covert.sh flow $1

T="$(date +%s)"
echo "Time in seconds: ${T}"

echo "Generating formal models ..."
./covert.sh dsl2 $1
echo "Solving formal models ..."
./covert.sh solver $1
echo "Generating vulnerability models ..."
./covert.sh policy $1
cd ../../
result=$(pwd)/app_repo/$1/$1.xml
echo -e 'Analysis Finished.\nDetected vulnerabilities are listed in' $result

echo "Time in seconds: ${T}"
echo “aaaaaaaaaaaaa”
T="$(($(date +%s)-T))"
echo "Time in seconds: ${T}"
