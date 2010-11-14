#!/usr/bin/python 

import os, sys, re

def sort_files(a,b):
  find_vol = lambda a: re.findall(r'/(\d+)(?:-\d+)?/(\d+)(?:-\d+)?/', a)[0]
  (vol_a, num_a) = find_vol(a)
  (vol_b, num_b) = find_vol(b)
  if vol_a == vol_b:
	return cmp(int(num_a), int(num_b))
  else:
	return cmp(int(vol_a), int(vol_b))

path = sys.argv[1]

global_index_path = path + os.sep + 'index.html'
global_index_file = open(global_index_path, "w+")

global_index_file.write('<html>\n<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /></head>\n<body>\n')

index_files = []
for dir, subdirs, files in os.walk(path):
  matched = filter(lambda s: s == 'index.txt', files)
  index_files.extend(['%s%s%s' % (dir, os.sep, f) for f in matched])

index_files.sort(sort_files)

has_journal_title = False
for index_fname in index_files:
  index_file = open(index_fname, 'r')
  
  if not has_journal_title:
	journal_title = index_file.readline()
	global_index_file.write('<h1>' + journal_title.strip() + '</h1>\n')
	has_journal_title = True
  else:
	index_file.readline()
	
  header = index_file.readline()
  global_index_file.write('<h2>' + header.strip() + '</h2>\n')
  
  index_file.readline()
  
  content_path = index_fname[:index_fname.rfind(os.sep)]
  
  while True:
	entry = index_file.readline()
	if not entry:
	  break
	  
	m = re.match(r'^(\d\d) - (.*) \[(.*)\]$', entry)
	content_file_path = content_path + os.sep + m.group(1) + '.pdf'
	title = m.group(2)
	author = m.group(3)
	  
	global_index_file.write('%s [<i>%s</i>]&nbsp;<a href="%s">&gt;&gt;</a><br/>\n' % (title, author, content_file_path))
  
  index_file.close()

global_index_file.write('</body>\n</html>\n')

global_index_file.close()
