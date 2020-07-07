# -*- coding:UTF-8 -*-

import re
import codecs
import urllib.request
from datetime import datetime
from datetime import timedelta
from urllib import parse

# import pandas as pd
# import numpy as np

class target_url_manager(object):
  """
  18  
  创建target_url_manager类，该类包含以下几个方法：
    * add_page_urls：解析股吧单页的HTML代码，获得该页的帖子URL
    * add_pages_urls：构建队列，讲全部页的帖子URL建立为二维list格式
    * has_page_url：判断队列是否为空
    * get_new_url：每次推出一页的帖子URL
  """

  def __init__(self, st_url):
    self.target_urls = list()
    self.store_urls = list()
    self.general_url = st_url
  
  def add_page_urls(self, i):
    item_urls = list()
    url = self.general_url + 'f_%d.html'%i
    # print(url)
    
    html_cont = urllib.request.urlopen(url).read().decode('utf-8')

    pattern = re.compile('/news\S+html', re.S)
    mews_comment_urls = re.findall(pattern, html_cont)

    # print('mews_comment_urls : ', mews_comment_urls)

    for comment_url in mews_comment_urls : 
      whole_url = parse.urljoin(self.general_url, comment_url)
      item_urls.append(whole_url)

    return item_urls

  def add_pages_urls(self, n):
    for i in range(1, n+1):
      self.target_urls.append(self.add_page_urls(i))
    
    self.target_urls.reverse()
    return

  def has_page_url(self):
    return len(self.target_urls) != 0

  def get_new_url(self):
    next_url = self.target_urls.pop()
    self.store_urls.append(next_url)

    # print('next_url : ', next_url)
    return next_url



class html_cont_analy(object):
  """
  单个帖子爬取的内容包括三部分，帖子发表时间、作者及帖子标题
  """

  def download(self,url):
    html_cont1 = urllib.request.urlopen(url).read().decode('utf-8')
    com_cont = re.compile(r'<div id="mainbody">.*?zwconttbn.*?<a.*?<font>(.*?)</font>.*?<div.*?class="zwcontentmain.*?">.*?"zwconttbt">(.*?)</div>.*?social clearfix',re.DOTALL)

    try:
      # cont=com_cont.search(html_cont1).group()
      conts = re.findall(com_cont, html_cont1)
      for item in conts:
        if (item[0]!=u"财经评论") and (item[0]!=u"东方财富网"):
          return u"散户ID-"+item[0] + item[1] + "\n"
        else:
          return u"官方-"+item[0] + item[1] + "\n"

    except Exception as e:
      print("NO HTML")
      return "NO HTML"

  def find_time(self,url):
    html_cont2 = urllib.request.urlopen(url).read().decode('utf-8')
    pub_elems = re.search('<div class="zwfbtime">.*?</div>',html_cont2).group()

    try:
      pub_time = re.search('\d\d\d\d-\d\d-\d\d',pub_elems).group()
      dt = datetime.strptime(pub_time,"%Y-%m-%d") # 字符串转时间格式
      return datetime.date(dt)
    
    except Exception as e:
      print("NO HTML")
      return datetime.now().date()+timedelta(days=1)



class output_txt(object):
  """
  打开文件、写文件和关闭文件
  """
  def open_txt(self):
    name = 'stock_cont.txt'
    try:
      f = codecs.open(name, 'a+', 'utf-8')
    except Exception as e:
      print('NO TXT')
    
    return f

  def out_txt(self, f_handle, conts):
    try:
      f_handle.write(conts)

    except Exception as e:
      print('NO FILE')

  def close_txt(self, f_handle):
    f_handle.close()




class crawer_task(object):
  def __init__(self):
    self.target_page = target_url_manager('http://guba.eastmoney.com/list,002372,')
    self.downloader = html_cont_analy()
    self.outputer = output_txt()

  def apply_run(self, sumpage):
    file_txt = self.outputer.open_txt()
    error_time = 0
    true_time = 0
    time_start = datetime.now().date()

    self.target_page.add_pages_urls(sumpage)

    while self.target_page.has_page_url():
      new_urls = self.target_page.get_new_url()

      for url in new_urls:
        if time_start <= (self.downloader.find_time(url) + timedelta(days=30)):
          self.outputer.out_txt(file_txt, self.downloader.download(url))
          true_time = true_time + 1
        
        else:
          error_time = error_time + 1
          if error_time >= 10: break

    print('%s has a sum of %d comments'%(time_start, true_time))
    self.outputer.close_txt(file_txt)
    return


if __name__ == '__main__':
  sumpage = 3
  obj_crawer = crawer_task()
  obj_crawer.apply_run(sumpage)
  

