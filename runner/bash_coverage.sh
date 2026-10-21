#!/bin/bash
# Jason Stys: original-file Bash tracing, not a rewritten target. File/line prefix only is retained.
# Arguments: $1 is a trusted per-case trace path; remaining arguments are the approved entry/argv.
# Local map: trace FD opened@L6; BASH_XTRACEFD@L8 routes traces; PS4@L9 carries source/line anchors. No functions.
set -eu
exec 9>"$1"
shift
export BASH_XTRACEFD=9
export PS4=$'\036${BASH_SOURCE[0]}:${LINENO}\037'
exec /bin/bash --noprofile --norc -x "$@"
