# This file contains the definitions for all the functions that are used and called in our code to run the webapp

# Importing all the libraries that will be needed to run the code for webapp

from pywebio.input import *
from pywebio.input import file_upload
from pywebio.input import textarea, input
from pywebio import start_server
from pywebio.output import put_text
from pywebio.output import *
from pywebio.session import *
import time
import pandas as pd
from pywebio.output import put_html, put_loading
from pywebio import start_server
import csv 
import re
from fpdf import FPDF
from IPython.core.display import HTML
from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import os
import warnings
warnings.simplefilter("ignore")

# We create a class WebApp since a lot of the functions use same variables so this way we can house all function definitions under a singular class for which we could just call an instance when running the code
class WebApp:

	# This will set up the basic environment for the webapp and allow user to select keywords of interest
	def run_app(self):

		# Configuring environment: title of page 
		set_env(title = "Intersectionality in Film and Television")

		# Welcome popup that closes with click 
		popup('Welcome to ~Lights, Camera, Python~ :)', [
		    put_button('Find something to watch!', onclick = close_popup)
		])

		# Keywords that user can select from 
		KEYWORDS = ['Select','activism', 'african-american', 'aging', 'asian-american', 'bisexual',
		             'childhood', 'childhood-trauma', 'class-differences', 'college', 'coming-of-age',
		             'disability', 'education', 'europe', 'experimental-film', 'gay', 'gay-parent',
		             'high-school', 'hispanic', 'homelessness', 'immigrant', 'independent-film', 
		             'indigenous', 'lesbian', 'lgbtq', 'mental-health', 'midlife-crisis',
		             'old-age', 'parenthood', 'poverty', 'sexual-orientation', 'student-film',
		             'transgender', 'wealth']

		# User keyword selection and "rank-by" selection
		self.interests_selection = input_group('What are your interests?', [
		                            select(label = 'Choose A Keyword', options = KEYWORDS, name = 'FirstKeyword'),
		                            select(label = 'Choose A Second Keyword (Optional)', options = KEYWORDS, name = 'SecondKeyword'),
		                            radio(label = 'Rank Results By', options = ['Most Popular', 'Highest Rated', 'Year of Release'], name = 'RankBy')
		                            ])

		# Save keywords into csv file disregarding "select" as a keyword and "rank-by" choice
		self.keywords = list(self.interests_selection.values())[:2]
		self.keywords = ([key for key in self.keywords if key != "Select"])
		df = pd.DataFrame(self.keywords, columns = ["column"])
		df.to_csv("keywords.csv", index=False)

		# Loading bar 
		put_processbar('bar')
		for i in range(1, 11):
		    set_processbar('bar', i / 10)
		    time.sleep(0.1)

		# Display Monsieur Mittens 
		put_text("Monsieur Mittens is making your watchlist!").style('color: black; font-family: "Free Mono"')   
		put_image(open('Cat-Movie.png', 'rb').read())

		# Message to show when user clicks on Monsieur Mittens message pop-up 
		def show_msg():
		    put_text('"am working v hard 2 make!"').style('color: black; font-family: "Free Mono"')  

		# Monsieur Mittens message pop-up 
		toast("Message from Monsieur Mittens", position = "right", duration=0, onclick=show_msg)

		put_markdown(":D")


	# This function will get us all the webpages for the movies and TV shows of our interest
	def get_pages(self):

		with requests.Session() as session:
		    
		    # For saving links 
		    self.all_links = []
		    
		    # Start on page 1 
		    page_number = 1
		    
		    # Link formatting if there is only 1 keyword
		    if len(self.keywords) == 1:
		        url = "https://www.imdb.com/search/keyword/?keywords=" + self.keywords[0] + "&ref_=fn_kw_kw_1"
		    
		    # Link formatting if there are 2 keywords
		    if len(self.keywords) == 2:
		    	url = "https://www.imdb.com/search/keyword/?keywords=" + self.keywords[0] + "%2C" + self.keywords[1] + '&ref_=kw_ref_key&sort=moviemeter,asc&mode=detail&page=1'

		    # Append url
		    while True:
		    	# Append url
		    	self.all_links.append(url)
		    	response = session.get(url)
		    	soup = BeautifulSoup(response.content, 'html.parser')

		    	# Check if there is next page, break if not
		    	next_link = soup.find('a', text = 'Next »')
		    	if next_link is None:
		    		break

		    	# Go onto next page
		    	url = urljoin(url, next_link['href'])
		    	page_number += 1


	# This function will get us the URLs for the posters of all the titles that will be displayed to the user
	def get_posters(self):

		# For storing movie posters 
		self.movie_posters = []

		for link in self.all_links:
		    html = urlopen(link)
		    bs = BeautifulSoup(html, 'html.parser')
		    
		    # Til limit of 50 results 
		    if len(self.movie_posters) < 50:
		        # Find all images on link 
		        images = bs.find_all('img')
		        for img in images:
		            # If it has the poster attribute, append 
		            if img.has_attr('loadlate'):
		                self.movie_posters.append(img['loadlate'])


	# This will convert the URLs fetched by the previous functions into actual images to be displayed in the table of recommendations to the user
	def create_images(self):

		# Create a dataframe using csv file
		df = pd.read_csv('movies.csv')

		# Assign posters list as new column of the dataframe
		df.insert(0, 'Poster', self.movie_posters[:df.shape[0]])

		# Rank dataframe by Highest rate if that was selected
		if list(self.interests_selection.values())[-1] == 'Highest Rated':
		    df = df.sort_values(by = ['Rating'], ascending = False)

		# Rank dataframe by Year of Release if that was selected
		if list(self.interests_selection.values())[-1] == 'Year of Release':
		    df = df.sort_values(by = ['Year'], ascending = False)
		    
		df.reset_index(drop = True, inplace = True)

		#Converting links to html tags
		def path_to_image_html(path):
		    return '<img src="'+ path + '" width="60" >'

		# Rendering the dataframe as HTML table
		df.to_html(escape=False, formatters=dict(Poster=path_to_image_html))

		# Rendering the images in the dataframe using the HTML method.
		HTML(df.to_html(escape=False,formatters=dict(Poster=path_to_image_html)))

		# Saving the dataframe as a webpage
		df.to_html('resultspage.html',escape=False, formatters=dict(Poster=path_to_image_html))


	# This function will display all the results, that is, movies and TV show recommendations to the user
	def display_results(self):

		# Message stating that results shown are for the specified keywords 
		put_text('"ah oui, here are you choices! enjoy!"').style('color: black; font-family: "Free Mono"') 
		if len(self.keywords) == 1:
		    put_text("Showing results for keyword" + self.keywords[0]).style('color: black; font-family: "Free Mono"') 

		if len(self.keywords) == 2:
		    put_text("Showing results for keywords " + self.keywords[0] + " and " + self.keywords[1] + ":").style('color: black; font-family: "Free Mono"') 

		# Display table 
		with open('resultspage.html', 'r') as f:
		    html = f.read()
		    put_html(html)

		put_markdown(":D")


	# This function will delete the movies.csv file created during the process of webscraping in order for the process to be repeated
	def delete_csv(self):
		os.remove('movies.csv')