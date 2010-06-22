# Some simple Wikipedia functions
# Released under the MIT license. Joshua Gross 2010
#
# This script has a lot of trouble processing movie titles like:
#  Intolerable.Cruelty.2004.Swesub.mp4
#
import urllib2
import os, re, xattr, sys

acceptable_page_chars = 'a-zA-Z0-9_\-,\(\)'
acceptable_page_chars_flex = 'a-zA-Z0-9_\-,\(\)\s'
wikipedia_read_pattern = re.compile(r'^http\://en.wikipedia.org/wiki/(.*)(\?.*)?$', re.IGNORECASE)
film_year_pattern = re.compile(r'(^(.*?)[^0-9]|^)([0-9]{4})([^0-9](.*?)$|$)', re.IGNORECASE)
wikipedia_redirect_pattern = re.compile(r'#REDIRECT \[\[(['+acceptable_page_chars_flex+']+)\]\]', re.IGNORECASE)
wikipedia_filmbox_pattern = re.compile(r'(\{\{Infobox film)', re.IGNORECASE)

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' 
fetch_headers = {'User-Agent' : user_agent} 

# Take a movie title and find a Wikipedia page for it
def find_movie_page(movie_title):
	movie_year = ''
	m = film_year_pattern.findall(movie_title)
	if (m != []):
		movie_year = m[0][2]
		movie_title = m[0][1] + m[0][4]

	# Search order:
	# name (year film)
	# name (film)
	# name (disambiguation)
	# name
	
	#TODO: parse directors/torrent names out of filename

	if movie_year:
		f = process_redirects(movie_title+' ('+movie_year+' film)')
		if is_film_page(f):
			return f

	f = process_redirects(movie_title+' (film)')
	if is_film_page(f):
		return f

	f = process_redirects(movie_title)
	if is_film_page(f):
		return f

	return ''

# Wikify a name
def wikify(title):
	return re.sub("[^"+acceptable_page_chars+"]", "_", title)

# Return 'edit' page for a given page
def edit_page(url):
	# Is URL a "read" page, not an "edit" page?
	m = wikipedia_read_pattern.findall(url)
	if m != []:
		url = 'http://en.wikipedia.org/w/index.php?title='+m[0][0]+'&action=edit'
	return url

# Get page at the end of redirects
def process_redirects(page_in):
	page = wikify(page_in)
	url = 'http://en.wikipedia.org/w/index.php?title='+page+'&action=edit'

	request = urllib2.Request(url, None, fetch_headers)
	result = urllib2.urlopen(request)
	s = result.read()

	m = wikipedia_redirect_pattern.findall(s)
	
	if (m != []):
		return process_redirects(m[0])

	return page

# Check to see if this is a valid film page
def is_film_page(page_in):
	page = wikify(page_in)
	url = 'http://en.wikipedia.org/w/index.php?title='+page+'&action=edit'

	request = urllib2.Request(url, None, fetch_headers)
	result = urllib2.urlopen(request)
	s = result.read()

	m = wikipedia_filmbox_pattern.findall(s)
	if (m == []):
		return 0
	else:
		return 1
