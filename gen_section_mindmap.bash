#!/usr/bin/env bash

# Generates a text file that can be imported into Simple MindMap Pro.
# You need to pass the section name, for example:
# ./gen_section_mindmap.bash sections/s_04_ai_practitioner  > my_section_map.txt

if  [[ -z ${1} || ! -d ${1} ]]
then
    echo "User error: Please pass a section directory name"
    echo "Example: ./gen_section_mindmap.bash sections/s_04_ai_practitioner > my_section_map.txt"
    echo "Exiting..."
    exit 1
fi

set -euo pipefail

section_dir="${1%/}"                # e.g. sections/s_04_ai_practitioner

# If you have a top level content.md at the section, you don't need this - begin
# base="${section_dir##*/}"           # s_04_ai_practitioner
# section="${base#s_[0-9]*_}"         # ai_practitioner
# section="${section//_/ }"           # ai practitioner
# printf '%s\n' "$section"
# If you have a top level content.md at the section, you don't need this - end


root_title="$(grep -m1 -E '^#[[:space:]]+' "$section_dir/content.md" | sed -E 's/^#[[:space:]]+//')"
printf '%s\n' "$root_title"

find "$section_dir" -mindepth 2 -maxdepth 2 -type f -name 'content.md' -print0 |
sort -zV |
xargs -0 awk '
function tabs(n,  i,s){s=""; for(i=0;i<n;i++) s=s "\t"; return s}
FNR==1 { cur=1 }
# keep your validation/matcher
$0 ~ /^(#{1,6}[[:space:]]+.*|- \*\*.*\*\*)/ {
  if ($0 ~ /^#{1,6}[[:space:]]+/) {
    match($0,/^#{1,6}/); lvl=RLENGTH
    t=$0; sub(/^#{1,6}[[:space:]]+/,"",t)
    print tabs(lvl) t      # chapter # is now child of root_title
    cur=lvl
    next
  }

  if ($0 ~ /^- \*\*.*\*\*/) {
    t=$0
    sub(/^- \*\*/,"",t)
    sub(/\*\*.*/,"",t)
    print tabs(cur+1) t
  }
}
'