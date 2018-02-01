# Get images from Google's Search API

This is a quick and dirty python script to fetch images from Google's search API and save them.

## Usage

```
python get.py -k YOUR_KEY -c YOUR_SEARCH_ENGINE -q YOUR_QUERY -p NUMBER_OF_PAGES
```

For more information on setting up a key and cx, read this [Stack Overflow post](https://stackoverflow.com/questions/34035422/google-image-search-says-api-no-longer-available).

* `-k` - Your key.
* `-c` - Your custom search engine.
* `-q` - The query to search for
* `-p` - (optional) Number of pages to fetch
* `-f` - (optional) extension to use. Default is `.jpg`

## Caching

Because Google limits requests to a 100 per day, this script aggressively caches responses from Google's API. All requests are saved as JSON files in the .cache/ directory.
