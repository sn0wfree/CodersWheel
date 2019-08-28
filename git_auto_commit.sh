#!/usr/bin/env bash
nowdate= `date`
python setup.py sdist

echo ${nowdate}

echo "${nowdate} daily backup at ${nowdate}"

echo "git marking"

git add *
git commit -m"Daily backup at ${nowdate}"
echo "will push !"

git push origin master