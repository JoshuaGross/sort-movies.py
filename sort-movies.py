#!/usr/local/bin/python
# Calling from command line: sort-movies.php /path/to/movie/directory
#
# Tested on Mac OS 10.6.
#
# Released under the MIT license. Joshua Gross 2010
#
#TODO: process subdirectories of movies
#TODO: create txt and html lists of movies: genre, actor, producer, director listings
#TODO: manual editing of attributes
import os, re, xattr, sys
from datetime import *
import time
import urllib2
from stat import *

# Config
movie_dir = sys.argv[1] # TODO: getopt
file_format = '{year} - {director} - {title}{dot_discno}'

# Constants
script_domain = 'com.joshisgross.py.sort-movies'
completeness_mark = ':tags_complete6'
url_mark = ':director'
director_mark = ':director'
actors_mark = ':actors'
movie_title_mark = ':title'
movie_year_mark = ':year'
movie_genre_mark = ':genre'
movie_producer_mark = ':producer'
movie_discno_mark = ':disc'
movie_url_mark = ':wikiurl'

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' 
fetch_headers = {'User-Agent' : user_agent} 

wikipedia_read_pattern = re.compile(r'^http\://en.wikipedia.org/wiki/(.*)(\?.*)?$', re.IGNORECASE)

video_file_pattern = re.compile(r'(.*)\.(avi|mp4|m4v|divx|mpeg)$', re.IGNORECASE)
director_match = re.compile(r'\|\s*director\s*\=\s*(?:\{\{Unbulleted list\|\{\{ubl\||)?\s*([^\r\n]+)\s*(?:\}\})?', re.IGNORECASE)
title_match = re.compile(r'\|\s*name\s*\=\s*([^\r\n]+)', re.IGNORECASE)
producer_match = re.compile(r'\|\s*producer\s*\=\s*(?:\{\{Unbulleted list\|\{\{ubl\||)?\s*([^\r\n]+)\s*(?:\}+)?', re.IGNORECASE)
actor_match = re.compile(r'\|\s*starring\s*\=\s*(?:\{\{Unbulleted list\|\{\{ubl\||)?\s*([^\r\n]+)\s*(?:\}+)?', re.IGNORECASE)
year_match = re.compile(r'\|\s*released\s*\=\s*\{\{start date\|([0-9]+)\|([0-9]+)\|([0-9]+)\}\}', re.IGNORECASE) # {start date} template
year_match2 = re.compile(r'\|\s*released\s*\=\s*[a-zA-Z]+\s*([0-9]{1,2}\,\s*)?([0-9]{4})', re.IGNORECASE) # year M D, Y
year_match3 = re.compile(r'\|\s*released\s*\=\s*\'+\[\[.*\]\]\:\'+\s*([0-9]{1,2}\s*)?[a-zA-Z]+\s*([0-9]{1,2}\,\s*)?([0-9]{4})', re.IGNORECASE) # multiple years
disc_no_match = re.compile(r'CD([0-9]+)', re.IGNORECASE)

# Name will match: names with or without [[ ]]; names separated by <br />; names listed as uncredited
# First parethenthesis: [[, ''', br, or beginning of string
# Second parenthesis: name, must not end in whitespace or single quote
# Third parenthesis: optional, some comment about name in parethentheses: (actor), (uncredited), etc; and pipe followed by link text
# Fourth parenthesis: ]], ''', optional
# Fifth parenthesis: same as third
# Sixth parenthesis: end-of-name marker: br, end of line, or pipe
name_match = re.compile(r'(\[\[|br />\s*|\'\'\'|\||^)([^\[\]\<\>\(\)\|\{\}]+[^\[\]\<\>\(\)\|\{\}\s\'])(\s*\([a-zA-Z]+\)\s*(\|[^\[\]\<\>]+)?)?(\'\'\'|\]\])?\s*(\([a-zA-Z]+\)\s*)?(\s*\|\s*|\&lt;|\s*$)', re.IGNORECASE)

# Common functions
def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]
def movie_get_tags(movie, attributes):
	movie_director = ''
	movie_title = ''
	movie_producer = ''
	movie_actors = ''
	movie_year = ''
	movie_genre = '' # no regex for this yet
	movie_discno = ''

	if (script_domain+movie_url_mark) not in attributes:
		url = raw_input("Wikipedia edit URL > ")
	else:
		url = attributes.get(script_domain+movie_url_mark)

	# Is URL a "read" page, not an "edit" page?
	m = wikipedia_read_pattern.findall(url)
	if m != []:
		url = 'http://en.wikipedia.org/w/index.php?title='+m[0][0]+'&action=edit'

	try:
		request = urllib2.Request(url, None, fetch_headers)
		result = urllib2.urlopen(request)
		s = result.read()

		m = year_match.findall(s)
		if m != []:
			movie_year = m[0][0]
		else:
			m = year_match2.findall(s)
			if m != []:
				movie_year = m[0][1]
			else:
				m = year_match3.findall(s)
				if m != []:
					movie_year = m[0][2]

		m = director_match.findall(s)
		if m != []:
			m2 = name_match.findall(m[0])
			for key, item in enumerate(m2):
				movie_director += (', ' if movie_director != '' else '') + m2[key][1]

		m = title_match.findall(s)
		if m != []:
			m2 = name_match.findall(m[0])
			for key, item in enumerate(m2):
				movie_title += (', ' if movie_title != '' else '') + m2[key][1]

		m = producer_match.findall(s)
		if m != []:
			m2 = name_match.findall(m[0])
			for key, item in enumerate(m2):
				movie_producer += (', ' if movie_producer != '' else '') + m2[key][1]

		m = actor_match.findall(s)
		if m != []:
			m2 = name_match.findall(m[0])
			for key, item in enumerate(m2):
				movie_actors += (', ' if movie_actors != '' else '') + m2[key][1]

		m = disc_no_match.findall(movie)
		if m != []:
			movie_discno = m[0]

	except urllib2.URLError, e:
		print(e)

	if movie_title == '':
		movie_title = raw_input("Movie title > ")
	else:
		print 'Movie title: ' + movie_title

	if movie_discno != '':
		print 'Disc number: ' + movie_discno

	if movie_director == '':
		movie_director = raw_input("Director > ")
	else:
		print 'Movie director: ' + movie_director

	if movie_producer == '':
		movie_producer = raw_input("Producer > ")
	else:
		print 'Movie producer: ' + movie_producer

	if movie_actors == '':
		movie_actors = raw_input("Lead Actors > ")
	else:
		print 'Lead actors: ' + movie_actors

	if movie_year == '':
		movie_year = raw_input("Year > ")
	else:
		print 'Year: ' + movie_year

	if movie_genre == '':
		movie_genre = raw_input("Genre > ")
	elif (script_domain+movie_genre_mark) in attributes and attributes.get(script_domain+movie_genre_mark) != '':
		movie_genre = attributes.get(script_domain+movie_genre_mark)
	else:
		print 'Genre: ' + movie_genre
	
	# TODO: functionalize all of the above
	# TODO: do not save unless all data confirmed by user

	attributes.set(script_domain + movie_url_mark, url)
	attributes.set(script_domain + director_mark, movie_director)
	attributes.set(script_domain + movie_producer_mark, movie_producer)
	attributes.set(script_domain + actors_mark, movie_actors)
	attributes.set(script_domain + movie_year_mark, movie_year)
	attributes.set(script_domain + movie_genre_mark, movie_genre)
	attributes.set(script_domain + movie_title_mark, movie_title)
	attributes.set(script_domain + movie_discno_mark, movie_discno)
	attributes.set(script_domain + completeness_mark, "true")

	return

if os.path.isdir(movie_dir) is True:
	movies = listdir_fullpath(movie_dir)
	for movie in movies:
		# Figure out what type of movie this is:
		# Directory?
		if os.path.isdir(movie) is True:
			print 'Found directory-movie, skipping for now'
		elif video_file_pattern.match(movie) is not None:
			file_attributes = xattr.xattr(movie)

			# Has this movie file already been processed?
			if (script_domain+completeness_mark) not in file_attributes:
				print "\033[1;31m" + 'Processing for first time: ' + movie + "\033[0m"
				movie_get_tags(movie, file_attributes)

			# If file attributes are complete, rename file
			if (script_domain+completeness_mark) in file_attributes:
				new_filename = file_format
				new_filename = new_filename.replace('{title}', file_attributes.get(script_domain+movie_title_mark))
				new_filename = new_filename.replace('{director}', file_attributes.get(script_domain+director_mark))
				new_filename = new_filename.replace('{year}', file_attributes.get(script_domain+movie_year_mark))
				discno = file_attributes.get(script_domain+movie_discno_mark)
				new_filename = new_filename.replace('{dot_discno}', ('.'+discno if discno != '' else ''))
				m = re.match('^(.*?/)([^/]+)(\.[^\./]+)$', movie)
				new_filename = re.sub('^(.*?/)([^/]+)(\.[^\./]+)$', m.group(1)+new_filename+m.group(3), movie)
				if new_filename != movie and os.path.exists(new_filename) is False:
					print "Renaming Movie: " + new_filename
					os.rename(movie, new_filename)
				else:
					print "Properly tagged: " + new_filename
				movie = new_filename

		#else:
			#print 'NOT A MOVIE: ' + movie
