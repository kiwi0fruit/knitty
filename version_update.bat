set tagname=0.2.2
git tag -d %tagname%
git push --delete origin %tagname%
git tag -a %tagname%
git push --tags
pause
:: pandoc README.md -o README.rst
