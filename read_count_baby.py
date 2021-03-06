#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import urllib.parse
import urllib.error
import re
import time
import sys
import random
from datetime import datetime
from http.cookiejar import CookieJar


#cookie获取html
def head_open_url(url):
	cookie = CookieJar() 
	opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor)
	opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.1708.400 QQBrowser/9.5.9635.400')]
	req = urllib.request.Request(url)
	page = opener.open(req)
	html = page.read().decode('utf-8')
	
	return html
	
	
#ip获取html	
def ip_open_url(url):

	# 要访问的目标页面
	targetUrl = url

	# 代理服务器
	proxyHost = "proxy.abuyun.com"
	proxyPort = "9010"

	# 代理隧道验证信息
	proxyUser = "H020J4Y3704H1X8D"
	proxyPass = "E0EBA2F2CF0A028E"

	proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
		"host" : proxyHost,
		"port" : proxyPort,
		"user" : proxyUser,
		"pass" : proxyPass,
	}

	proxy_handler = urllib.request.ProxyHandler({
		"http"	: proxyMeta,
		"https" : proxyMeta,
	})

	#cookie = CookieJar()
	
	opener = urllib.request.build_opener(proxy_handler)#,urllib.request.HTTPCookieProcessor)
	opener.addheaders = [("Proxy-Switch-Ip", "yes")]
	opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.1708.400 QQBrowser/9.5.9635.400')]

	urllib.request.install_opener(opener)
	page = urllib.request.urlopen(targetUrl,timeout = 10)
	html = page.read().decode('utf-8')
	
	return html

		
#根据名称获取对应url
def get_top_url(top_name):
	top_urlname = urllib.parse.quote(top_name) #把中文转成url编码
	name_url = 'http://weixin.sogou.com/weixin?type=1&query=%s&ie=utf8&_sug_=n&_sug_type_='%top_urlname
	name_real_url =''
	
	i = 0
	while i < 5:
	
		try:

			name_html = ip_open_url(name_url)#打开url
			p = re.compile('href="([^"]*)"><em><!--red_beg-->' + top_name + '<!--red_end--></em></a>')
			#搜索到公众号并成功获取url
			if p.search(name_html):
				name_real_url = p.search(name_html).group(1).replace('amp;','')
				break
			#未搜索到公众号
			elif '/new/pc/images/bg_404_2.png' in name_html:
				print('sorry,没有"%s"这个公众号的数据'%top_name)
				break
			#在搜索公众号的时候被antispider发现了
			else:
				print(top_name + ':antispider---' + 'get_top_url')
				i += 1
				if i == 5:
					print('pass')


			
		#此IP不好使，换一个
		except urllib.error.HTTPError as e:
			pass
		except urllib.error.URLError as e:
			pass
		except TimeoutError as e:
			pass
		except OSError as e:
			pass

		
	return name_real_url

	
#获取排行榜需要部分的数据，返回一个二维列表	
def get_top(html,n1,n2):
	
	#需要匹配的REs
	p1 = re.compile(r'class="name">[^<]+\D+[^<]+\D+[^<]+\D+[^<]+\D+[^<]+\D+[^<]+\D+[^<]+\D+[^<]+')
	p2 = re.compile(r'</?td>\D*')

	#处理html，得到可用数据
	top_list = p1.findall(html)
	for i in range(len(top_list)):
		top_list[i] = p2.sub('_',top_list[i])
		top_list[i] = top_list[i].replace('class="name">','')
	
	top_list = top_list[n1-1:n2]
	for i in range(len(top_list)):
		top_list[i] = top_list[i].split('_')
	
	return top_list


#把列表转换成字典，便于对比		
def list_to_dict(list):
	listto_dict = {}
	for i in range(len(list)):
		listto_dict[list[i][0]] = list[i][1]
	return listto_dict	
	
	
#把时间字符串转换为时间戳
def time_to_stamp(time_str):
	time_list = time_str.split('-')
	time_convert = datetime(int(time_list[0]),int(time_list[1]),int(time_list[2]))
	return time_convert.timestamp()

	
#获取公众号某段时间内的实际发布文章数，返回main/all的字符串
def get_factdata(html,start,end):
	
	#需要匹配的REs
	p1 = re.compile(r'"datetime":\d+')
	p2 = re.compile(r'"author"')
	p3 = re.compile(r'"app_msg_ext_info"')
	
	#匹配时间戳，反向输出序列
	article_time_list = p1.findall(html)
	for i in range(len(article_time_list)):
		article_time_list[i] = int(article_time_list[i][11:21])
	article_time_list_stol = article_time_list[::-1]
	
	article_start = ''
	article_end = ''
	
	#获得开始位置的时间戳
	for each in article_time_list_stol:
		if each >= start:
			article_start = str(each)
			break
	#获得结束位置的时间戳
	for each in article_time_list_stol:
		if each >= end:
			article_end = str(each)
			break
	
	#获得匹配的时间内的数据
	article_start_pos = html.find(article_start)
	article_end_pos = html.find(article_end)
	html_need = html[article_start_pos:article_end_pos]
	
	list_allneed = p2.findall(html_need)
	list_mainneed = p3.findall(html_need)
	main_all = '%s/%s'%(len(list_mainneed),len(list_allneed))
	
	return main_all


#数据比较	
def campare_data(list,dict):
	fact_data_list = list
	top_data_dict = dict
	compare_list = []
	for i in range(len(fact_data_list)):
		fact_data_list[i] = fact_data_list[i].split(':')
		if top_data_dict[fact_data_list[i][0]] == fact_data_list[i][1]:
			temp_y = '符合-yes   %s:   真实-%s   统计-%s'%(fact_data_list[i][0],fact_data_list[i][1],fact_data_list[i][1])
			compare_list.append(temp_y)
		else:
			temp_n = '符合-no    %s:   真实-%s   统计-%s'%(fact_data_list[i][0],fact_data_list[i][1],top_data_dict[fact_data_list[i][0]])
			compare_list.append(temp_n)
			
	return compare_list
			
			
#主函数
def read_main():	
	
	#秀恩爱
	anwser = input('你是不是马傲雪(yes/no):')
	if anwser == 'yes':
		print('I LOVE U')
		print('好好工作~')
	else:
		print('好好工作别偷懒,马总监在看着你')
	
	#得到时间宽度(倒叙)
	find_end_str = input('请输入需要查找的开始时间(xxxx-xx-xx):')
	find_end = time_to_stamp(find_end_str)
	find_start_str = input('请输入需要查找的结束时间(xxxx-xx-xx):')
	find_start = time_to_stamp(find_start_str) + 86400
	
	#获取前n名的数据
	n1 = int(input('排行榜开始名次(1-100):'))
	n2 = int(input('排行榜结束名次(1-100):'))
	
	#url
	url = "http://www.wxranking.com/pubranking/week.html?scode=babybook"
	each_url = ''
	final_list_ele = ''
	
	#得到榜单数据的list和dict
	top_list = get_top(head_open_url(url),n1,n2)
	print('获取排行榜正常')
	compare_dict = list_to_dict(top_list)
	
	final_list = []
	top_num = n1
	
	for name in top_list:
		each_url = get_top_url(name[0]) #用代理ip能正确读出url
		#搜索到了公众号
		if each_url:
			while 1:
				try:
					each_html =	ip_open_url(each_url)
					if '验证码' in each_html:
						pass
						#print(name[0] + ':antispider---重试')
					else:
						break

				except urllib.error.HTTPError as e:
					pass
				except urllib.error.URLError as e:
					pass
				except TimeoutError as e:
					pass
				except OSError as e:
					pass

			main_all = get_factdata(each_html,find_start,find_end)

			final_list_ele = '%s:%s'%(name[0],main_all)
			print('%s.'%top_num,final_list_ele)
		#搜索不到公众号
		else:
			print('%s.%s:未搜索到该公众号'%(top_num,name[0]))
			final_list_ele = '%s:未找到'%(name[0])
		
		with open('final_baby.txt','a') as f:
			f.write('%s.'%top_num + final_list_ele + '\n')
		
		top_num += 1 #排名

		time.sleep(1) #延时1秒

	#为了避免发生异常程序中断，所以从数据完全取得后，再进行比较
	do_compare = input("是否进行比较(yes/no):")
	
	if do_compare == 'yes':
		with open('final_baby.txt','r') as f:
			for each in f.readlines():
				each = each.strip()
				final_list.append(each.split('.')[1])
		
		#得到比较结果		
		campare_list = campare_data(final_list,compare_dict)

		with open('comparebaby.txt','w') as f:
			num = 1
			for each in campare_list:
				f.write('%s.'%num + each + '\n')
				num += 1
		print('获取比较数据功能正常,数据保存在与程序相同文件夹的comparebaby.txt文件中')			
	
	print('program over')


#运行	
if __name__ == '__main__':	  
	read_main()