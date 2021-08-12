#!/usr/bin/python
import argparse
import requests
from bs4 import BeautifulSoup
import itertools
from tabulate import tabulate
import logging

from pdb import set_trace as bp
logging.basicConfig()
logger = logging.getLogger(__file__)

class CarParser():
    """
    Scrape carspecs.us for car data
    """
    def __init__(self, make, year=None, model=None):
        """
        CarParser constructor

        @param make: Required string
        @param year: Optional string
        @param model: Optional string
        """
        self.URL   = 'https://www.carspecs.us/cars'
        self.year  = year
        self.make  = make
        self.model = model

    def scrape(self):
        """
        Based on supplied year/model/make
            - Generate URL
            - Call appropriate scraper helper function
            - Return result
        """
        result = None
        if self.model and self.year:
            self.URL += '/{year}/{make}/{model}'.format(year=self.year, make=self.make, model=self.model)
            result = self.scrape_full()
        elif self.model:
            self.URL += '/{make}/{model}'.format(make=self.make, model=self.model)
            result = self.scrape_year()
        elif self.year:
            self.URL += '/{year}/{make}'.format(year=self.year, make=self.make)
            result = self.scrape_model()
        else:
            self.URL += '/{make}'.format(make=self.make)
            result = self.scrape_model_year()
        return result

    def scrape_year(self):
        """
        When make and model are given but not year.
        Result will be a list of valid years
        """
        result = None
        head = requests.head(self.URL)
        if head.ok:
            get = requests.get(self.URL) 
            soup = BeautifulSoup(get.content, "html.parser")
    
            years = [ li.find('a') for li in soup.findAll('li') if '/%s/%s' % (self.make,self.model) in li.find('a')['href'] ]
            years = [ year.text.strip(' \n\t') for year in years ]
            if len(years) == 0:
                logger.error("No such %s model: %s" % (self.make, self.model))
    
            headers = [ 'year' ]
            table = [ i for i in itertools.zip_longest(years) ]
            result = tabulate(table, headers=headers)
        else:
            logger.error("HTTP %d: %s" % (head.status_code, URL))
        return result
    
    def scrape_model(self):
        """
        When make and year are given but not model
        Result will be a list of valid models
        """
        result = None
        head = requests.head(self.URL)
        if head.ok:
            get = requests.get(self.URL) 
            soup = BeautifulSoup(get.content, "html.parser")
    
            models = [ li.find('a') for li in soup.findAll('li') if '/cars/%s/%s' % (self.year,self.make) in li.find('a')['href'] ]
            models = [ model.text.strip(' \n\t') for model in models ]
            if(len(models) == 0):
                logger.error("No %s made in year: %s" % (self.make, self.year))
    
            headers = [ 'model' ]
            table = [ i for i in itertools.zip_longest(models) ]
            result = tabulate(table, headers=headers)
        else:
            logger.error("HTTP %d: %s" % (head.status_code, self.URL))        
        return result
    
    def scrape_model_year(self):
        """
        When make is given but neither make nor model
        Result will be a list of valid years and models
        """
        result = None
        head = requests.head(self.URL)
        if head.ok:
            get = requests.get(self.URL) 
            soup = BeautifulSoup(get.content, "html.parser")
    
            years = [ li.find('a') for li in soup.findAll('li') if ((li.find('a').text.isnumeric()) and not '/cars/%s' % (self.make) in li.find('a')['href']) ]
            models = [ li.find('a') for li in soup.findAll('li') if '/cars/%s' % (self.make) in li.find('a')['href'] ]
            years = [ year.text.strip(' \n\t') for year in years ]
            models = [ model.text.strip(' \n\t') for model in models ]
            if (len(years)==0) or (len(models)==0):
                logger.error("No such car make: %s" % (self.make))
    
            headers = [ 'year', 'model' ]
            table = [ i for i in itertools.zip_longest(years, models) ]
            result = tabulate(table, headers=headers)
        else:
            logger.error("HTTP %d: %s" % (head.status_code, self.URL))
        return result
    
    def scrape_full(self):
        """
        Called when year/make/model are all given
        Result will be keys and values of scraped fields
        """
        result = None
        keys = []
        values = []
    
        head = requests.head(self.URL)
        if head.ok:
            get = requests.get(self.URL) 
            soup = BeautifulSoup(get.content, "html.parser")

            if soup.find('div', class_="main-car-details"):
                blob = soup.find('div', class_="main-car-details")
                if blob.find('span'):
                    price = blob.find('span').text.strip()
                    keys.append('price')
                    values.append(price)
                    if blob.find('span').next_sibling.next_sibling:
                        mileage = blob.find('span').next_sibling.next_sibling.strip()
                        keys.append('mileage')
                        values.append(mileage)
                elif blob.text:
                    mileage = blob.text.strip()
                    keys.append('mileage')
                    values.append(mileage)

            if soup.find('div', class_="car-details"):
                blob = soup.find('div', class_="car-details").findAll('div', class_="pure-u-1 pure-u-md-1-2")
                keys.extend([ d.findNext('h4').text.strip(' \r\n\t') for d in blob ])
                values.extend([ d.findNext('h4').next_sibling.strip(' \r\n\t') for d in blob ])

            if len(values) > 0:
                headers = [ 'key', 'value']
                table = [ i for i in itertools.zip_longest(keys, values) ]
                result = tabulate(table, headers=headers)
            else:
                logger.error("Bad URL: %s" % (self.URL))
        else:
            logger.error("HTTP %d: %s" % (head.status_code, self.URL))
        return result    

if __name__ == '__main__':
    cli = argparse.ArgumentParser(description='Scrape some car data')
    cli.add_argument('--make', type=str, help='Make of car ie: [Toyota, Honda, Ford]', required=True)
    cli.add_argument('--model', type=str, help='Model of car ie: [Corolla, Civic, F150]')
    cli.add_argument('--year', type=int, help='year of car ie: [2020, 2001, 1969]')
    #cli.add_argument('--trim', type=str, help='Trim of car ie: sport')
    args = cli.parse_args()

    car_parser = CarParser(args.make, args.year, args.model)
    result = car_parser.scrape()
    print(result)
