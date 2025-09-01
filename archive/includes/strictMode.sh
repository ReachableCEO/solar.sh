#!/bin/bash


function StrictMode()
{

# Standard strict mode and error handling boilderplate..

# This is a function I include and execute in every shell script that I write. 
# It sets up a bunch of error handling odds and ends

# Bits and pieces Sourced from (as best I recall):
# * https://news.ycombinator.com/item?id=24727495
# * many other hacker news / slashdot etc posts over the years
# * https://www.tothenew.com/blog/foolproof-your-bash-script-some-best-practices/
# * https://translucentcomputing.com/2020/05/unofficial-bash-strict-mode-errexit/
# * http://redsymbol.net/articles/unofficial-bash-strict-mode/
# * the school of hard knocks... (aka my code failures...)

#Here's the beef (as the commercial says..)

#use errexit (a.k.a. set -e) to make your script exit when a command fails.
#add || true to commands that you allow to fail.
set -o errexit

# Use set -o nounset (a.k.a. set -u) to exit when your script tries to use undeclared 
# variables.
set -o nounset

#Use set -o pipefail in scripts to catch (for example) mysqldump fails 
#in e.g. mysqldump |gzip. 
#The exit status of the last command that threw a non-zero exit code is returned
set -o pipefail

#Function tracing...
set -o functrace


export PS4='(${BASH_SOURCE}:${LINENO}): - [${SHLVL},${BASH_SUBSHELL},$?] $ '

}