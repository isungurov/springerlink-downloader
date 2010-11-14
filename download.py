#!/usr/bin/python
import urllib2
import re
import sys
import os


USER_AGENT = 'Mozilla/5.0 (X11; U; Linux x86_64; ru; rv:1.9.2.12)'
TIMEOUT = 120

if len(sys.argv) < 2:
  print 'Usage: %s <springerlink_id>' % (sys.argv[0])
  sys.exit(1)


def fetch(*args):
  print '/'.join(args)
  while True:
    try:
      req = urllib2.Request('/'.join(args), headers={'User-Agent': USER_AGENT})
      f = urllib2.urlopen(req, timeout=TIMEOUT)
      content = f.read()
      break
    except:
      continue

  return content  

class SpringerLinkDownloader:

  SPRINGERLINK_HOST = 'http://www.springerlink.com'
  CONTENT_PATH = '/content'
  CONTENT_URL = SPRINGERLINK_HOST + CONTENT_PATH

  def __init__(self, journal_id):
    self.journal_id = journal_id
  
  def __find_all_numbers(self, pattern, text):
    all = re.findall(pattern, text)
    unique = list(set(all))
    return unique
  
  def download_journal(self):
    journal_content = fetch(self.CONTENT_URL, self.journal_id)

    volumes = self.__find_all_numbers('"' + self.CONTENT_PATH + '/' + self.journal_id + r'/(\d+)/"', journal_content)
    self.journal_title = re.findall(r'<h1 lang="en" class="title">\s+(.*)\s+</h1>', journal_content)[0].strip()
    
    print self.journal_title
    
    for vol in volumes:
      self.download_volume(vol)
  
  def download_volume(self, volume):
    self.volume = volume
    print 'Volume', volume
    
    volume_content = fetch(self.CONTENT_URL, self.journal_id, volume)
    
    numbers = self.__find_all_numbers('"' + '/'.join((self.CONTENT_PATH, self.journal_id, volume)) + r'/([\d-]+)/"', volume_content)
    
    for num in numbers:
      self.download_number(num)
    
  def download_number(self, number):
    self.number = number
    print '  Number', number, ':',
    
    number_content = fetch(self.CONTENT_URL, self.journal_id, self.volume, number)
    
    self.number_date = re.findall(r'<h2 class="filters">\s*<a href=".*" title=".*">.*</a>, .* / (.*)\s*</h2>', number_content)[0].strip()
    
    articles = re.findall(r'<p class="title"><a href="([^"]*)/">(.*)</a></p><p class="authors">(.*)</p>', number_content)

    self.number_path = os.sep.join((self.journal_title, self.volume, number))
    self.index_file = self.open_index_file()
    
    article_number = 1
    for (content_path, title, authors_content) in articles:
      print '.',
      sys.stdout.flush()
      self.download_article(article_number, content_path, title, authors_content)
      article_number += 1
  
    print ''
    self.index_file.close()

  def open_index_file(self):
    if not os.path.exists(self.number_path):
      os.makedirs(self.number_path)
    
    number_index_path = os.sep.join((self.number_path, 'index.txt'))
    if not os.path.exists(number_index_path):    
      index_file = open(number_index_path, 'w+')
      
      index_file.write(self.journal_title + '\n')
      index_file.write('Volume ' + str(self.volume))
      index_file.write(' / ')
      index_file.write('Number ' + str(self.number))
      index_file.write(' (' + self.number_date + ')\n\n')
    else:
      index_file = open(number_index_path, 'a+')  
      
    return index_file

  def download_article(self, article_number, content_path, title, authors_content):
    authors = re.findall(r'<a title=".*" href=".*">(.*)</a>(?: and <a title=".*" href=".*">(.*)</a>)+', authors_content)
    if authors:
      authors = authors[0]
    else:
      authors = re.findall(r'<a title=".*" href=".*">(.*)</a>', authors_content)
    
    article_number_str = '%02d' % (article_number)
    
    article_file_name = os.sep.join((self.number_path, article_number_str + '.pdf'))
    if os.path.exists(article_file_name):
      return
    
    article_file = open(article_file_name, 'w+')
    
    article_content = fetch(self.SPRINGERLINK_HOST, content_path, 'fulltext.pdf')
    
    article_file.write(article_content)
    article_file.close()
    
    self.index_file.write(article_number_str)
    self.index_file.write(' - ')
    self.index_file.write(title)
    self.index_file.write(' [' + ', '.join(authors) + ']')
    self.index_file.write('\n')  


d = SpringerLinkDownloader(sys.argv[1])
d.download_journal()
    
