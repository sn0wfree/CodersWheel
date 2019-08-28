#!/usr/bin/env bash
nowdate= `date`
python setup.py sdist

#echo ${nowdate}

echo "${nowdate} daily backup at ${nowdate}"

echo "git marking"

git add *
git commit -m"Daily backup at ${nowdate}"

branch_name=`git symbolic-ref --short -q HEAD`
echo "will push ${branch_name}!"

git push origin ${branch_name}