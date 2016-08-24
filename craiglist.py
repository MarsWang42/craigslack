from craigslist import CraigslistForSale
from slackclient import SlackClient
from dateutil.parser import parse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.orm import sessionmaker
import sys
import traceback
import time
import settings


engine = create_engine('sqlite:///listings.db', echo=False)

Base = declarative_base()


class Listing(Base):
    """
    A table to store data on craigslist listings.
    """

    __tablename__ = 'listings'

    id = Column(Integer, primary_key=True)
    link = Column(String, unique=True)
    created = Column(DateTime)
    geotag = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    name = Column(String)
    price = Column(Float)
    location = Column(String)
    cl_id = Column(Integer, unique=True)
    area = Column(String)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


def in_box(coords, box):
    """
    Helper function to check whether a result's coords to be inside of an area or not
    :param coords: the post's coordinates
    :param box: target area
    :return: True of False
    """
    if box[0][0] < coords[0] < box[1][0] and box[0][1] < coords[1] < box[1][1]:
        return True
    return False


def slack_message(result):
    """
    Helper function to send message to selected slack team
    :param result: the data being sent
    """
    sc = SlackClient(settings.SLACK_TOKEN)
    desc = "{0} | {1} | {2} | <{3}>".format(result["area"], result["price"], result["name"], result["url"])
    sc.api_call(
        "chat.postMessage", channel=settings.SLACK_CHANNEL, text=desc,
        username='CraiglistBot', icon_emoji=':robot_face:'
    )


def scrape_for_sale():
    """
    Searching target object in craiglist for sale
    """

    cl_h = CraigslistForSale(site=settings.CRAIGSLIST_SITE, category=settings.CRAIGSLIST_CATEGORY,
                             filters={'query': settings.CRAIGSLIST_FORSALE_SECTION,
                                      'search_titles': True,
                                      'max_price': settings.MAX_PRICE})

    gen = cl_h.get_results(sort_by='newest', geotagged=True)
    results = []

    while True:
        try:
            result = next(gen)
        except StopIteration:
            break
        except Exception:
            continue

        # Search the result in database, if it is already there, skip it.
        listing = session.query(Listing).filter_by(cl_id=result["id"]).first()
        if listing is None:
            geotag = result["geotag"]
            area_found = False
            area = ""
            lat = 0
            lon = 0
            if result["geotag"] is not None:
                lat = geotag[1]
                lon = geotag[0]
            coords = (lat, lon)
            for a, box in settings.BOXES.items():
                if in_box(coords, box):
                    area = a
                    area_found = True
            result["area"] = area

            # Try parsing the price.
            price = 0
            try:
                price = float(result["price"].replace("$", ""))
            except Exception:
                pass

            # Create the listing object.
            listing = Listing(
                link=result["url"],
                created=parse(result["datetime"]),
                lat=lat,
                lon=lon,
                name=result["name"],
                price=price,
                location=result["where"],
                cl_id=result["id"],
                area=result["area"],
            )

            # Save the listing so we don't grab it again.
            session.add(listing)
            session.commit()

            # if the location can be found in the box, append it into the results
            if area_found:
                results.append(result)

    return results


def do_scrape():
    """
    Runs the craigslist scraper, and posts data to slack.
    """

    # Get all the results from craigslist.
    all_results = scrape_for_sale()

    print("{}: Got {} results".format(time.ctime(), len(all_results)))

    # Post each result to slack.
    for result in all_results:
        slack_message(result)

if __name__ == "__main__":
    while True:
        print("{}: Starting scrape cycle".format(time.ctime()))
        try:
            do_scrape()
        except KeyboardInterrupt:
            print("Exiting....")
            sys.exit(1)
        except Exception as exc:
            print("Error with the scraping:", sys.exc_info()[0])
            traceback.print_exc()
        else:
            print("{}: Successfully finished scraping".format(time.ctime()))
        time.sleep(settings.SLEEP_INTERVAL)
