# Get images from Google's Search API

This is a quick and dirty python script to fetch images from Google's search API and save them.

Google limits results to only the first 100 from a search, so keep that in mind when querying for images.

## Usage

```
python get.py -k YOUR_KEY -c YOUR_SEARCH_ENGINE -q YOUR_QUERY -p NUMBER_OF_PAGES -out outDir -e jpg -f outFile
```

Or for multiple queries:

```
python get.py -k YOUR_KEY -c YOUR_SEARCH_ENGINE -q query1,query2,query3 -p NUMBER_OF_PAGES
```

For more information on setting up a key and cx, read this [Stack Overflow post](https://stackoverflow.com/questions/34035422/google-image-search-says-api-no-longer-available).

* `-k` - Your key.
* `-c` - Your custom search engine.
* `-q` - The query to search for. Specify multiple queries to search for by separating them with commas.
* `-p` - (optional) Number of pages to fetch.
* `-e` - (optional) extension to use. Default is `.jpg`.
* `-out` - (optional) The directory where images are saved. Defaults to `/images`.
* `-f` - (optional) The filename to save the image at. Defaults to the search query.

## Caching

Because [Google limits requests to 100 search queries per day for free](https://developers.google.com/custom-search/json-api/v1/overview?hl=en_US#pricing), this script aggressively caches responses from Google's API. All requests are saved as JSON files in the .cache/ directory.
