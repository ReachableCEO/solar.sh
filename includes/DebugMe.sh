function DebugMe() {
 [[ $script_debug = 1 ]] && "$@" || :

#to turn debugging on, set script_debug=1
#to turn debugging off, set script_debug=0

# be sure to append || : or || true here or use return 0, since the return code
# of this function should always be 0 to not influence anything else with an unwanted
# "false" return code (for example the script's exit code if this function is used
# as the very last command in the script)

#This function does nothing when script_debug is unset or empty, but it executes the 
#given parameters as commands when script_debug is set. Use it like this:

#debugme logger "Sorting the database"
#database_sort
#debugme logger "Finished sorting the database, exit code $?"


# * print commands to be executed to stderr as if they were read from input 
# (script file or keyboard)
# * print everything before any ( substitution and expansion, …) is applied
set -v

# * print everything as if it were executed, after substitution and expansion is applied
# * indicate the depth-level of the subshell (by default by prefixing a + (plus) sign to 
# the displayed command)
# * indicate the recognized words after word splitting by marking them like 'x y'
# * in shell version 4.1, this debug output can be printed to a configurable file 
#descriptor, rather than sdtout by setting the BASH_XTRACEFD variable.
set -x

}
