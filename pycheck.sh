#!/bin/bash
# Test code formatting compliance.
# So far only python3 supported.

echo
echo "======================"
echo "Python (v3) code check"
echo "======================"


find . -not -path '*/.*' | grep '.*.py$' > changed_files.txt

# Only Added and modified files are checked.
while read -r fname; do
  ext="${fname##*.}"
  if [[ "${ext}" == "py" ]]; then
    echo "* Checking ${fname}"
    pylint --rcfile="pylint3.rc" "${fname}"
  fi
done < "changed_files.txt"
