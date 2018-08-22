#!/bin/bash
cat *.txt > tmp_all.txt
echo "All doubles get listed between the following two lines:"
echo "-------------------------------"
perl -ne 'print if $SEEN{$_}++' < tmp_all.txt
echo "-------------------------------"
echo "done checkin doubles."
rm tmp_all.txt
