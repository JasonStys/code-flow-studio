#!/bin/bash
# Jason Stys: original-file Bash tracing, not a rewritten target. File/line prefix only is retained.
# Arguments: $1 is a trusted per-case trace path; remaining arguments are the approved entry/argv.
set -eu
exec 9>"$1"
shift
export BASH_XTRACEFD=9
export PS4=$'\036${BASH_SOURCE[0]}:${LINENO}\037'
exec /bin/bash --noprofile --norc -x "$@"
