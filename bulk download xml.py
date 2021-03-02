import concurrent
import functools
import json
import os
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
import requests
import shutil
import concurrent.futures
import requests, zipfile, io

def download_file(r,target_path,xmlfile):

    with open(target_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=512):
            fd.write(chunk)
    zipfile = ZipFile(target_path)
    zipfile.extract(xmlfile)

def read_dict(file_name):
    f = open(file_name, 'r')
    files_by_year = json.loads(f.read())
    return files_by_year

years = [2001,2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
files_by_year = read_dict('files_by_year.txt')

session = requests.Session()
for year in years:
    for file in files_by_year[str(year)]:
        if '.zip' in file and '_r1' not in file and '_r2' not in file:
            url = 'https://bulkdata.uspto.gov/data/patent/application/redbook/fulltext/' + str(year) + '/' + file

            index = file.find(".zip")
            r = session.get(url, stream=True)
            r.raise_for_status()

            xmlfile = file[:index] + str(".xml")

            download_file(r, file, xmlfile)

            os.remove(file)

            new_file = open(file[:index] + str("-new.xml"), "w")
            new_file.write("<root>\n")

            with open(xmlfile, 'r') as f:
                for line in f:
                    if line != '<?xml version="1.0" encoding="UTF-8"?>\n' and '!DOCTYPE' not in line and "!ENTITY" not in line and line != "]>\n":
                        new_file.write(line)

            new_file.write("\n</root>\n")
            new_file.close()


            if os.path.exists(xmlfile):
                os.remove(xmlfile)
            else:
                print("The file does not exist")

            print("Done: "+str(file))
