# -*- coding: utf-8 -*-
import re
from base64 import b64decode

NAME = "History Channel"
ICON = "icon-default.png"
ART = "art-default.jpg"
BASE_URL = "http://www.history.com"

####################################################################################################

def Start():
	Plugin.AddPrefixHandler("/video/historychannel", MainMenu, NAME, ICON, ART)

	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
	Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")

	ObjectContainer.title1 = NAME
	ObjectContainer.art = R(ART)
	ObjectContainer.view_group = 'List'

	DirectoryObject.thumb = R(ICON)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON)

	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:10.0) Gecko/20100101 Firefox/10.0"

####################################################################################################

def MainMenu():
	oc = ObjectContainer()
	for show in HTML.ElementFromURL(BASE_URL+'/shows').xpath("//div[@id='all-shows-accordion']//div[@class='header']/span[@class='has-video']/preceding-sibling::span"):
		showVideos = show.xpath('./parent::div/following-sibling::div[@class="content clearfix"]/div[@class="info"]//a[@class="watch more"]')[0].get('href')
		if show.xpath('./parent::div/following-sibling::div[@class="content clearfix"]/ul[@class="nav"]/li')[0].text != None:
			oc.add(DirectoryObject(
				key = Callback(GetVideos, path = showVideos),
				title = show.text))
		else:
			showMainPage = show.xpath('./parent::div/following-sibling::div[@class="content clearfix"]/ul[@class="nav"]/li/a[@class="more"]')[0].get('href')
			oc.add(DirectoryObject(
				key = Callback(GetVideos, path = showVideos, showMainPage = showMainPage),
				title = show.text,
				art = Callback(GetBackground, path = showMainPage)))
	return oc

####################################################################################################

def GetBackground(path):
	try:
		page = HTTP.Request(BASE_URL+path).content
		bkgnd = page[page.find('background: url(')+16:]
		bkgnd = bkgnd[:bkgnd.find(')')]

		logo = HTML.ElementFromString(page).xpath('//div[@class="logo"]//img')[0].get('src')
		if logo == None:
			return DataObject(HTTP.Request('http://www.plexapp.tv/plugins/history/?image='+bkgnd, cacheTime=CACHE_1MONTH), 'image/jpeg')
		else:
			return DataObject(HTTP.Request('http://www.plexapp.tv/plugins/history/?image='+bkgnd+'&logo='+logo, cacheTime=CACHE_1MONTH), 'image/jpeg')
	except:
		return Redirect(R(ART))

####################################################################################################

def GetVideos(path, showMainPage = None):
	if showMainPage != None:
		oc = ObjectContainer(view_group = "InfoList", art = Callback(GetBackground, path=showMainPage))
	else:
		oc = ObjectContainer(view_group = "InfoList")

	page = HTTP.Request(BASE_URL+path).content
	mrssdata = re.search('mrssData =[ ]+"([^"]+)', page).group(1)
	mrssdata =  String.Unquote(b64decode(mrssdata)).replace('media:','media-')

	for category in XML.ElementFromString(mrssdata).xpath("//item"):
		video_url = category.xpath('./link')[0].text +'#'+ category.xpath('./media-category')[0].text

		title = category.xpath('./title')[0].text
		summary = category.xpath('./description')[0].text
		thumb = category.xpath('./media-thumbnail')[0].get('url')
		duration = int(category.xpath('./media-content')[0].get('duration')) * 1000

		oc.add(VideoClipObject(
	        url = video_url,
	        title = title,
	        summary = summary,
	        thumb = Callback(GetThumb, path = thumb),
	        duration = duration))

	if len(oc) == 0:
		return MessageContainer("No Videos", "There aren't any videos available for this show")
	return oc

####################################################################################################

def GetThumb(path, thumb_type = "image/jpeg"):
	if (path != None):
		try:
			return DataObject(HTTP.Request(path, cacheTime=CACHE_1MONTH), thumb_type)
		except:
			pass

	return Redirect(R(ICON))
