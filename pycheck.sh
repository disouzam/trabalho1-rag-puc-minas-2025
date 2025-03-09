#!/bin/bash
# Test code formatting compliance.
# So far only python3 supported.

echo
echo "======================"
echo "Python (v3) code check"
echo "======================"


find . -not -path '*/.*' | grep '.*.py$' > python_files.txt
rm pylint_check.txt

# Only Added and modified files are checked.
while read -r fname; do
  ext="${fname##*.}"
  if [[ "${ext}" == "py" ]]; then
    echo "* Checking ${fname}"
    pylint --rcfile="pylint3.rc" "${fname}"
    pylint --rcfile="pylint3.rc" "${fname}" >> pylint_check.txt
  fi
done < "python_files.txt"
