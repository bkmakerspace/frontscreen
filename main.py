import pygame
import json

from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from cefpython3 import cefpython as cef

from PIL import Image, PILLOW_VERSION

import threading

from urllib import parse
from datetime import datetime

pygame.display.init()
pygame.font.init()

pygame.mouse.set_visible(False)

size = [1920,1080]
done = False
clock = pygame.time.Clock()

cefSettings = {
    "windowless_rendering_enabled": True,
}

cefSwitches = {
    "disable-gpu":"",
    "disable-gpu-compositing":"",
    "enable-begin-frame-scheduling":"",
    "disable-surfaces":"",
}

cef.Initialize(settings=cefSettings, switches=cefSwitches)

def getLineWrap(text, width, font):
    # determine maximum width of line
    i=0
    while font.size(text[:i])[0] < width and i < len(text):
        i += 1
    # if we've wrapped the text, then adjust the wrap to the last word      
    j = i
    if i < len(text): 
        j = text.rfind(" ", 0, i) + 1
    if j > 10:
        i = j
    return text[i:],text[:i]

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        encoded = self.rfile.read(int(self.headers['Content-Length']))
        try:
            encoded = encoded.decode('ascii')
        except:
            pass
        data = json.loads(encoded)
        if self.path == '/chat':
            theChat.append(data['name'],data['chat'])
        return

class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

class Chat:
    def __init__(self,width,height,chatsize=60):
        self.width = width
        self.height = height
        self.size = width,height
        self.surface = pygame.Surface(self.size,pygame.HWSURFACE)
        self.chatSize = chatsize
        self.lines = []
        self.font = pygame.font.SysFont('ubuntu',18)
        self.surface.fill((0,0,0))
    def append(self,user,chat):
        text = chat.strip().replace("\r"," ").replace("\n"," ")
        name = user+' '
        userWidth = self.font.size(name)[0]
        messageWidth = self.width - userWidth-20
        j = 0
        while text:
            text,line = getLineWrap(text,messageWidth,self.font)
            self.lines.append((name,userWidth,line))
            name = ""
            j+=1
            if j>=self.chatSize-1:
                break
        while len(self.lines)>self.chatSize:
            self.lines.pop(0)
    def render(self):
        chatSurface = pygame.Surface((self.width-20,self.height-20),pygame.HWSURFACE)
        chatSurface.fill((0,0,0))
        for i,line in enumerate(self.lines):
            user = self.font.render(line[0],True,(0,255,255),(0,0,0))
            message = self.font.render(line[2],True,(255,255,255),(0,0,0))
            chatSurface.blit(user,(0,i*self.font.get_linesize()))
            chatSurface.blit(message,(line[1],i*self.font.get_linesize()))
        self.surface.blit(chatSurface,(10,10))

class Clock:
    def __init__(self,width,height):
        self.width = width
        self.height = height
        self.size = width,height
        self.surface = pygame.Surface(self.size,pygame.HWSURFACE)
        self.font = pygame.font.SysFont('ubuntumono',80)
        self.time = 0
    def render(self):
        self.surface.fill((50,50,50))
        time = datetime.now().strftime('%I:%M %p')
        clock = self.font.render(time,True,(0,255,255),(50,50,50))
        w = clock.get_width()
        h = clock.get_height()
        x = (self.width/2)-(w/2)
        y = (self.height/2)-(h/2)
        self.surface.blit(clock,(x,y))

class RenderHandler(object):
    def __init__(self,width,height):
        self.OnPaint_called = False
        self.width = width
        self.height = height
        self.size = width,height
        self.surface = pygame.Surface(self.size,pygame.HWSURFACE)
    def OnLoadError(self, browser,frame,error_code, failed_url, **_):
        if not frame.IsMain():
            return
        print("failed to load main frame for url: {url}".format(url=failed_url))
    def GetViewRect(self, rect_out, **_):
        rect_out.extend([0,0,self.width,self.height])
        return True
    def OnPaint(self,browser,element_type,paint_buffer, **_):
        if element_type == cef.PET_VIEW:
            buffer_string = paint_buffer.GetBytes(mode="rgba",origin="top-left")
            self.surface.blit(pygame.image.frombuffer(buffer_string,self.size,"RGBA"),[0,0])

class Frame:
    def __init__(self,width,height):
        self.width = width
        self.height = height
        self.size = width,height
        self.surface = pygame.Surface(self.size,pygame.HWSURFACE)
    def render(self):
        self.surface.fill((25,25,25))

class HelloFrame(Frame):
    def __init__(self,width,height):
        Frame.__init__(self,width,height)
        self.font = pygame.font.SysFont('ubuntu',60)
        self.textWelcome = self.font.render("Welcome", True, (255,255,255),(25,25,25))
        self.textTo = self.font.render("to B&K Makerspace", True, (255,255,255),(25,25,25))
    def render(self):
        Frame.render(self)
        welcomeh = self.textWelcome.get_height()
        welcomew = self.textWelcome.get_width()
        toH = self.textTo.get_height()
        tow = self.textTo.get_width()
        welcomex = (self.width/2) - (welcomew/2)
        welcomey = (self.height/2) - (welcomeh)
        tox = (self.width/2) - (tow/2)
        toy = (self.height/2)
        self.surface.blit(self.textWelcome,[welcomex,welcomey])
        self.surface.blit(self.textTo,[tox,toy])

class CEFFrame(Frame):
    def __init__(self,width,height,url):
        Frame.__init__(self,width,height)
        self.url = url
        self.window_info = cef.WindowInfo()
        self.window_info.SetAsOffscreen(0)
        self.browser = cef.CreateBrowserSync(window_info=self.window_info,url=url)
        self.renderHandler = RenderHandler(self.width,self.height)
        self.browser.SetClientHandler(self.renderHandler)
        self.browser.SendFocusEvent(True)
        self.browser.WasResized()
    def render(self):
        Frame.render(self)
        self.surface.blit(self.renderHandler.surface,[0,0])
    def quit(self):
        self.browser.CloseBrowser()

class Card:
    def __init__(self,width,height):
        self.width = width
        self.height = height
        self.size = width,height
        self.surface = pygame.Surface(self.size,pygame.HWSURFACE)
        self.title = ''
    def render(self):
        title = pygame.font.SysFont('ubuntu',15,bold=True).render(self.title,True,(0,0,0),(180,180,180))
        self.surface.fill((180,180,180))
        x = (self.width/2)-(title.get_width()/2)
        y = 5
        self.surface.blit(title,[x,y])

class PrinterCard(Card):
    def __init__(self,width,height):
        Card.__init__(self,width,height)
        self.printers = []
        self.title = 'Printers'
    def addPrinter(self,name,baseTopic):
        pass;
    def render(self):
        Card.render(self)



server = ThreadingSimpleServer(('0.0.0.0',8080), Handler)

if __name__ == '__main__':
    screen = pygame.display.set_mode(size)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    theChat = Chat(400,840,33)
    
    theClock = Clock(400,150)

    blankFrame = HelloFrame(1430,728)
    #browserFrame = CEFFrame(1430,728,'http://google.com')

    blankCard = Card(262,262)

    printerCard = PrinterCard(262,262)
    while not done:
        clock.tick(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        theChat.render()
        theClock.render()
        blankFrame.render()
        blankCard.render()
        cef.MessageLoopWork()
        #browserFrame.render()
        printerCard.render()
        screen.fill((70,70,70))
        screen.blit(theChat.surface,[30,30])
        screen.blit(theClock.surface,[30,900])
        screen.blit(blankFrame.surface,[460,30])
        screen.blit(blankCard.surface,[460,788])
        screen.blit(blankCard.surface,[752,788])
        screen.blit(blankCard.surface,[1044,788])
        screen.blit(blankCard.surface,[1336,788])
        screen.blit(blankCard.surface,[1628,788])
        pygame.display.flip()
    server.shutdown()
    pygame.quit()
    #browserFrame.quit()
    cef.QuitMessageLoop()

