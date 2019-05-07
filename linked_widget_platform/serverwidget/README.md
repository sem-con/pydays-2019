# Twitter Server widget for LinkedWidgets.org

## Configure

`pip install -r requirements.txt`

if running on linkedwidgets.org or local instance (Netty WAMP router), ping/pong is not supported yet which will cause connection to the router dropped when ping timeout. 
To mitigate this issue, comment out line 835 (`self.dropConnection(abort=True)` in the `onAutoPingTimeout` method) in file autobahn/websocket/protocol.py in the python package dir.

## Running Server widget

### Start Server widget

`python twidget.py -router ws://linkedwidgets.org:28980/lwrouter`

or use 

`python twidget.py -router ws://localhost:28980/lwrouter` 

for [local LinkedWidgets instance](https://github.com/linkeddatalab/LWP-IntroSW)

### Serve Client widget interface 

put index.html in the accessible HTTP server or simply run `python -m http.server 8000` in this directory

### Register widget in the LinkedWidgets page
- open linkedwidgets.org (or local instance)
- in the "Home Page" tab, go to bottom right form (pick up widgets)
- use any name for the widget (e.g. `twitter`) and paste in URL of the widget (e.g. http://localhost:8000/ if you ran the above command)
- pick other widgets ([RML](http://pebbie.org/mashup/widget/rml?src=seismic7d), [Map](http://pebbie.org/mashup/widget/newmap), [JSON Viewer](http://linkedwidgets.org/widgets/JsonViewerWidget/index.html)), and click on "Quick mashup"
- drag and drop widgets from the left sidebar palette on the canvas
- connect terminals (`RML` to `Map`, `Map` to `twitter`, `twitter` to `JSON Viewer`)
- run it