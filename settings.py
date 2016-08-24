## Price

# The minimum price you want to pay for the good.
MIN_PRICE = 2

# The maximum priceyou want to pay for the good.
MAX_PRICE = 20

## Location preferences

# The Craigslist site you want to search on.
# For instance, https://orangecounty.craigslist.org is Orange County.
# You only need the beginning of the URL.
CRAIGSLIST_SITE = 'orangecounty'

## Category prefences

# Only goods of this category will be searched
CRAIGSLIST_CATEGORY = 'fua' # furniture

# A list of neighborhoods and coordinates that you want to look for the goods in.  Any listing that has coordinates
# attached will be checked to see which area it is in.  If there's a match, it will be annotated with the area
# name.  If no match, the neighborhood field, which is a string, will be checked to see if it matches
# anything in NEIGHBORHOODS.
BOXES = {
    "Irvine": [
        [-117.965355, 33.587167],
        [-117.703743, 33.780289],
    ],
}

## Search keyword preferences

# The key word of the good you're looking for.
CRAIGSLIST_FORSALE_SECTION = 'chair'

## System settings

# How long we should sleep between scrapes of Craigslist.
# Too fast may get rate limited.
# Too slow may miss listings.
SLEEP_INTERVAL = 20 * 60 # 20 minutes


# Any private settings are imported here.
try:
    from private import *
except Exception:
    pass

# Any external private settings are imported from here.
try:
    from config.private import *
except Exception:
    pass