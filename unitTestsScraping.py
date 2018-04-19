from lobsterScrap import *
import unittest, re
import pandas as pd

class TestStringMethods(unittest.TestCase):

	def test_numProductsInUSA(self):
		print("Running test_numProductsInUSA")

		#USA TEST
		country = "USA"
		outputFile = "outputLobsterTEST" + country + ".csv"
		startScraping(country,outputFile)
		df = pd.read_csv(outputFile,encoding='ISO-8859-1')
		self.assertEqual(len(df), 28)


	def test_fillFieldsInUSA(self):
		print("Running test_fillFieldsInUSA")

		#USA TEST
		country = "USA"
		outputFile = "outputLobsterTEST" + country + ".csv"
		#startScraping(country,outputFile)
		df = pd.read_csv(outputFile,encoding='ISO-8859-1')

		self.assertFalse(df.isnull().any().any())

	def test_urlFieldsInUSA(self):
		print("Running test_urlFieldsInUSA")

		#USA TEST
		#Regex to check if is a URL
		regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

		country = "USA"
		outputFile = "outputLobsterTEST" + country + ".csv"
		#startScraping(country,outputFile)
		df = pd.read_csv(outputFile,encoding='ISO-8859-1')


		dfURLRegex = df["URL"].apply(lambda x: re.match(regex, x) is not None)

		dfImageRegex = df["Image"].apply(lambda x: re.match(regex, x) is not None)

		self.assertTrue(dfURLRegex.all())

		self.assertTrue(dfImageRegex.all())

if __name__ == '__main__':
    unittest.main()