from bs4 import BeautifulSoup
import csv, string, sys, json
import requests
import re
import pandas as pd

#Version 1 for Lobster Scraping - Test Project

def getSizeText(text):
	#Getting the text of the Size Field
	sizeNumberIndex = 0
	text = text.strip()
	return text.split("-")[sizeNumberIndex].strip()

def getIfIsSoldProduct(text):
	#Getting if the currently size is sold out
	soldIndex = 1
	text = text.strip()
	textParts = text.split("-")
	if len(textParts) > 1:
		text = textParts[soldIndex].strip()
		return "sold" in text.lower()
	else:
		return False

def getTextColumn(soupTextElement):
	#Getting the text of the currently tag, and no from child tags
	return soupTextElement.find(text=True,recursive=False).strip()

def getTextPriceColumn(soupPriceElement):
	#Getting the text of Price Field, the last h2 tag have the currently price, in some cases, they show the older price
	soupPrices = soupPriceElement.find_all("h2")
	return soupPrices[len(soupPrices)-1].text.strip()

def getUrlImageColumn(soupImageElement):
	#Getting the url of the image field
	return soupImageElement["src"]

def getSizesColumn(soupSizesElement):
	#Getting Sizes and Sold Out Fields, in some cases, the product does not have Sizes
	sizes = []
	soldSizes = []
	if soupSizesElement != None:
		soupSizes = soupSizesElement.find_all("option")
		if len(soupSizes) > 0:
			#The initial index is 1 because the first option is the Select Tag
			initialIndex = 1
			for indexSize in range(initialIndex,len(soupSizes)):
				sizeText = soupSizes[indexSize].text
				sizes.append(getSizeText(sizeText))
				soldSizes.append(getIfIsSoldProduct(sizeText))

	return sizes,soldSizes


def getDetailsProduct(domainUrl,productUrl,cookies,ubicationsColumns):
	#Get html from the url
	html_text = requests.get(domainUrl + productUrl,cookies=cookies).text
	soup = BeautifulSoup(html_text, 'html.parser')

	#Instance the data for every column
	dataColumns = {}

	for columnName in ubicationsColumns.keys():
		#Getting the part of the html depending of the ubication in the JSON file
		soupColumn = soup.find(ubicationsColumns[columnName]["tag"],ubicationsColumns[columnName]["attributes"])

		#Check the type for every column and have a special treatment depending of the type
		if ubicationsColumns[columnName]["type"] == 'text':
			dataColumns[columnName] = getTextColumn(soupColumn)

		elif ubicationsColumns[columnName]["type"] == 'textPrice':
			dataColumns[columnName] = getTextPriceColumn(soupColumn)
		
		elif ubicationsColumns[columnName]["type"] == 'urlImage':
			dataColumns[columnName] = domainUrl + getUrlImageColumn(soupColumn)
		
		elif ubicationsColumns[columnName]["type"] == 'selectSizes':
			sizes,soldSizes = getSizesColumn(soupColumn)

			#Json syntax is used for the Sizes and Sold Out Fields to be sopported by CSV field
			dataColumns[columnName] = json.dumps(sizes)
			dataColumns[ubicationsColumns[columnName]["flags"]] = json.dumps(soldSizes)

		else:
			#Error Case
			dataColumns[columnName] = None

	return dataColumns

def downloadProducts(columnsCSV,domainUrl,sectionUrl,cookies,ubicationsColumns,outputFile):
	#Get html from the url
	html_text = requests.get(domainUrl + sectionUrl, cookies=cookies).text
	
	#Using BeautifulSoup for get the tags quickly
	soup = BeautifulSoup(html_text, 'html.parser')

	#Iterate between the products in the main page
	for productSoup in soup.find_all("div", {"class": "product-grid"}):
		#Getting the relative url of the product
		productUrl = productSoup.find("a")["href"]
		
		#Getting the data of the columns to put in the CSV
		dataColumns = getDetailsProduct(domainUrl,productUrl,cookies,ubicationsColumns)
		
		#Adding URL column
		dataColumns["URL"] = domainUrl + productUrl

		dfProduct = pd.DataFrame(dataColumns,columns=columnsCSV, index=[0])

		#Appending the product in the file written before, in case of a fail connection or a banned, the information will be in the file at some point
		with open(outputFile, "a") as f:
			dfProduct.to_csv(f, header=None, index=False,encoding='ISO-8859-1')


def startScraping(country,outputFile):
	domainUrl = 'https://www.lobstersnowboards.com'
	sectionUrl = '/shop/'

	#Read a json with the cookies from different countries
	with open('cookies.json', "r") as f:
		cookies = json.load(f)


	#CSV header
	columnsCSV = ["URL","Name","Image","Price","Sizes","Sold Out"]

	#Read a json with the ubications of the html for every column in the CSV file
	with open('ubicationColumns.json', "r") as f:
		ubicationsColumns = json.load(f)

	dfProducts = pd.DataFrame(columns=columnsCSV)

	#Write CSV file header
	with open(outputFile, "w") as f:
		dfProducts.to_csv(f, header=True, index=False,encoding='ISO-8859-1')

	downloadProducts(columnsCSV,domainUrl,sectionUrl,cookies[country],ubicationsColumns,outputFile)


def main():
	country = "USA"
	outputFile = "outputLobster" + country + ".csv"
	startScraping(country,outputFile)

if __name__ == '__main__':
    main()