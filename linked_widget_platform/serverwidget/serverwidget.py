"""file serverwidget.py

provide base class for developing widget job object
and widgetContainer for connecting to router

to use, extend BaseWidget and override run

```
import serverwidget as sw

class MyServerWidget(sw.BaseWidget):
    def run(self):
        pass

if __name__=="__main__":
    sw.connect(u'ws:127.0.0.1:8080/ws', u'realm1')

```
author paryan
date 10.11.2017
updated 01.05.2019
"""
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
import json
from timeit import default_timer as timer
from datetime import timedelta
"""
a widget is formulated as function with n inputs and a single output

it is represented as an object with n subscription channels and 1 publishing channel

each widget has a proxy which expose some methods:
- {id}_setup            : to create instance or connect a terminal
- {id}_destroy          : to remove the instance
- {id}_run              : to trigger execution, assuming all necessary inputs are received
- {id}_output           : to inspect the last produced output
- {id}_getRunningInfo   : to get runtime information (execution time)

when an input of A is connected to another widget B, it subscribe to the output topic of B
"""

class BaseWidget:
    """
    Base class for server widgets
    """
    def run(self):
        # !override this
        # returns dict
        pass

    #######################
    #   protected
    #######################
    def onInput(self, i, value):
        print ("onInput", i, value)
        self.inputs[i] = value

    def configure(self, kwargs):
        class Channel:
            def __init__(self, parent, sub, idx):
                self.parent = parent
                self.value = None
                self.idx = idx
                self.sub = sub
                d = self.parent.client.subscribe(self.__input, sub)
                d.addCallback(self.cb)
                
            def __input(self, msg):
                print (self, msg)
                self.value = msg
                self.parent.inputs[self.idx] = msg
                self.parent.tryRun()
            def cb(self, msg):
                print (msg)

        self.params = json.loads(kwargs['params']) if 'params' in kwargs else {}
        
        self.in_connections = kwargs['subscribers'] if 'subscribers' in kwargs else []
        self.in_channels = []
        for i, x in enumerate(self.in_connections):
            if x is not None:
                print ("subscribing channel ", repr(x))
                self.in_channels.append(Channel(self, x, i))
            else:
                self.in_channels.append(None)
        print (self.in_channels)
        self.inputs = [None for x in self.in_connections]

        self.token = kwargs['token']
        
        self.runningInfo = {}
        
        self.output = {}
        
        self.hashValue = ''
        if 'params' in kwargs:
            if not isinstance(kwargs['params'], dict):
                kwargs['params'] = json.loads(kwargs['params'])
            self.id = kwargs['params']['id']
        self.user = kwargs['user'] if 'user' in kwargs else ''

    def tryRun(self):
        # check if all inputs are filled
        # if yes then invoke widget.run()
        print (self.inputs)
        for i in self.inputs:
            if i is None:
                return ""
        self.runningInfo['startRunningTime'] = timer()
        result = self.run()
        self.runningInfo['stopTime'] = timer()
        self.runningInfo['runningTime'] = str(timedelta(self.runningInfo['stopTime']-self.runningInfo['startRunningTime']))
        if result is not None:
            self.returnOutput(result)
        return ""

    def getInfo(self):
        return self.runningInfo

    def returnOutput(self, value):
        self.output = value
        self.client.publish(self.token, value)

from twisted.internet import reactor
# \cond private
class WidgetContainer(ApplicationSession):
    """
    """
    def __init__(self, config):
        super(WidgetContainer, self).__init__(config)

        extra = config.extra
        self.id = extra['id']
        self.widgetClass = extra['widgetCls']

        # list of instances
        self.widgets = {}

    def onJoin(self, details):
        print(self.id+" connected ")
        print(details)
        
        def setup(message):
            print(self.id+"_setup called")
            print(message)
            msg = json.loads(message)
            token = msg['token']
            # check if all inputs are filled
            # if yes then invoke widget.run()oken']

            if token in self.widgets.keys():
                del self.widgets[token]
            
            widget = self.widgetClass()
            widget.client = self
            widget.configure(msg)
            
            self.widgets[token] = widget
            print (self.widgets.keys())
            run(message)
            return ""

        def destroy(message):
            try:
                print(self.id+"_destroy called")
                token = json.loads(message)['token']
                if token in self.widgets:
                    del self.widgets[token]
                    print ("widget",token,"removed")
                else:
                    print ("widget",token,"not exists")
            finally:
                return ""

        def run(message):
            print(self.id+"_run called")
            print(message)
            token = json.loads(message)['token']
            return self.widgets[token].tryRun()

        def info(message):
            print(self.id+"_getRunningInfo called")
            print (message)
            token = json.loads(message)['token']
            if token in self.widgets:
                d = self.widgets[token].getInfo()
                print(d)
            else:
                d = dict()
            d['instances'] = list(self.widgets.keys())
            return json.dumps(d)

        def output(message):
            print(self.id+"_output called")
            print( message)
            if message in self.widgets:
                return json.dumps(self.widgets[message].output)
            else:
                return "null"
        
        def cb(details):
            print(details)

        try:
            self.register(setup, 
                u"{}_setup".format(self.id))

            self.register(destroy, 
                u"{}_destroy".format(self.id))

            self.register(run, 
                u"{}_run".format(self.id))
            
            self.register(output, 
                u"{}_output".format(self.id))
            
            self.register(info, 
                u"{}_getRunningInfo".format(self.id))
           
            print("procedures registered") 
        except BaseException as e:
            print("failed to register procedure: {}".format(e))
       
    def onDisconnect(self):
        print("disconnected")
        if reactor.running:
            reactor.stop() 
# \cond

def connect(url, realm, widgetId, WidgetClass):
    runner = ApplicationRunner(
        url=url, realm=realm, extra=dict(
            id=widgetId, widgetCls=WidgetClass), max_retries=-1)
    runner.run(WidgetContainer)
        
if __name__ == "__main__":
    connect(
        #u"ws://linkedwidgets.org:28980/lwrouter", #LinkedWidgets instance
        #u"ws://localhost:28980/lwrouter", #local LinkedWidgets instance
        u"ws://localhost:8080/ws", #local crossbar router
        u"realm1",
        BaseWidget.__name__,
        BaseWidget)
