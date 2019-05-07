from __future__ import print_function
from serverwidget import BaseWidget, connect
import json
import twitter
import dateutil.parser as parser
import datetime
import time
import argparse
import twidgetconfig as cfg

class Twidget(BaseWidget):
  def __init__(self):
    self.api = twitter.Api(consumer_key=cfg.KEY,
                      consumer_secret=cfg.SECRET,
                      access_token_key=cfg.TOKEN,
                      access_token_secret=cfg.TOKEN_SECRET)
    print (self.api.VerifyCredentials())

  def run(self):
    print(self.params)
    query = "q={}&count={}".format(self.params['q'], self.params['limit'])
    print(query)
    results = self.api.GetSearch(raw_query=query)
    rjson = {
      "@context": "https://www.w3.org/ns/activitystreams",
      "@graph":[]
    }
    for x in results:
      tj = x._json
      ts = date = parser.parse(tj["created_at"]).isoformat()
      tweet = {
        "@id":u"https://twitter.com/{}/{}".format(tj[u"user"][u"screen_name"], tj[u'id_str']),
        "content":tj["text"],
        "actor": u"https://twitter.com/{}".format(tj[u"user"][u"screen_name"]),
        "type":"Note",
        "updated": ts
        }
      rjson["@graph"].append(tweet)
      print(json.dumps(x._json, indent=2))
      print(json.dumps(rjson, indent=2))
    return json.dumps(rjson)

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('-router', default=u"ws://localhost:28980/lwrouter", help="WAMP router address")
  parser.add_argument('-realm', default=u"realm1", help="realm of WAMP")

  args = parser.parse_args()
  connect(
      #u"ws://linkedwidgets.org:28980/lwrouter",
      args.router,
      args.realm,
      "twidget",
      Twidget)