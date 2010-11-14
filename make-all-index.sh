#!/bin/sh
for j in *
do
  if [ -d "$j" ]
  then
	cd "$j"
	../make-index.py .
	cd ..
  fi
done