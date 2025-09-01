#!/bin/bash

function PreflightCheck()
{

#Common things I check for in the scripts I write.

#export curr_host="$(hostname)"
#export curr_user="$USER"
#export host_check="$(echo $curr_host | grep -c <desired hostname>)"
#export user_check="$(echo $curr_user | grep -c <desired username>)"

#if [ $host_check -ne 1 ]; then
#    echo "Must run on <desired host>."
#    error_out
#fi

#if [ $user_check -ne 1 ]; then
#    echo "Must run as <desired user>."
#    error_out
#fi

#if [ "$ARG_COUNT" -ne <the right num> ]; then
#    help
#    error_out
#fi

#Your additional stuff here...
echo "All checks passed...."

}
