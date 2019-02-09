import pygame
import json

from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading

from urllib import parse
from datetime import datetime
from time import mktime

pygame.display.init()
pygame.font.init()

pygame.mouse.set_visible(False)

size = [1920,1080]
done = False
clock = pygame.time.Clock()

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
        if self.path == '/welcome':
            helloFrame.setCenter(data['text'],data['timeout'])
        if self.path == '/member':
            memberPresence.updateMember(data['member'],data['present'])
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

class Frame:
    def __init__(self,width,height):
        self.width = width
        self.height = height
        self.size = width,height
        self.surface = pygame.Surface(self.size,pygame.HWSURFACE)
        self.title = "Frame"
    def input(self,pos):
        pass
    def render(self):
        self.surface.fill((25,25,25))

class MemberFrame(Frame):
    def __init__(self,width,height,proc):
        Frame.__init__(self,width,height)
        self.font = pygame.font.SysFont('ubuntu',60)
        self.titleText = self.font.render("Members Present:", True, (255,255,255),(25,25,25))
        self.proc = proc
    def render(self):
        Frame.render(self)
        titleh = self.titleText.get_height()
        titlew = self.titleText.get_width()
        titlex = (self.width/2) - (titlew/2)
        titley = (titleh)
        self.surface.blit(self.titleText,[titlex,titley])


class HelloFrame(Frame):
    def __init__(self,width,height):
        Frame.__init__(self,width,height)
        self.font = pygame.font.SysFont('ubuntu',60)
        self.textWelcome = self.font.render("Welcome", True, (255,255,255),(25,25,25))
        self.centerEntry = ""
        self.centerTimeout = 0
        self.textTo = self.font.render("to B&K Makerspace", True, (255,255,255),(25,25,25))
    def setCenter(self,text,timeout):
        if timeout == 0:
            # Used to clear out messages
            self.centerEntry = ""
            self.centerTimeout = 0
        if self.centerTimeout > mktime(datetime.now().timetuple()):
            # Don't override existing messages.  Keeps the door control from overriding long term messages
            return
        self.centerEntry = text
        self.centerTimeout = mktime(datetime.now().timetuple())+timeout
    def render(self):
        Frame.render(self)
        welcomeh = self.textWelcome.get_height()
        welcomew = self.textWelcome.get_width()
        toh = self.textTo.get_height()
        tow = self.textTo.get_width()
        welcomex = (self.width/2) - (welcomew/2)
        welcomey = (self.height/2) - (welcomeh)
        tox = (self.width/2) - (tow/2)
        centery = (self.height/2)
        if self.centerTimeout > mktime(datetime.now().timetuple()):
            toy = (self.height/2) + (toh)
            centerText = self.font.render(self.centerEntry,True, (255,255,255),(25,25,25))
            centerx = (self.width/2) - (centerText.get_width()/2)
            self.surface.blit(centerText,[centerx,centery])
        else:
            toy = centery
        self.surface.blit(self.textWelcome,[welcomex,welcomey])
        self.surface.blit(self.textTo,[tox,toy])

class Card:
    def __init__(self,width,height):
        self.width = width
        self.height = height
        self.size = width,height
        self.surface = pygame.Surface(self.size,pygame.HWSURFACE)
        self.title = ''

    def render(self):
        title = pygame.font.SysFont('ubuntu',25,bold=True).render(self.title,True,(0,0,0),(180,180,180))
        self.surface.fill((180,180,180))
        x = (self.width/2)-(title.get_width()/2)
        y = 5
        self.surface.blit(title,[x,y])

class MemberPresence():
    def __init__(self):
        self.members = []
        self.count = 0
    def updateMember(self,name,present):
        if present:
            if name in self.members:
                return
            else:
                self.members.append(name)
        else:
            try:
                index = self.members.index(name)
                del self.members[index]
            except:
                pass

        pass;

class PresenceCard(Card):
    def __init__(self,width,height,presence):
        Card.__init__(self,width,height)
        self.title = 'Members'
        self.members = presence
    def render(self):
        Card.render(self)
        count = pygame.font.SysFont('ubuntu',180,bold=False).render(str(len(self.members.members)),True,(0,0,0),(180,180,180))
        x = (self.width/2)-(count.get_width()/2)
        y = 60
        self.surface.blit(count,[x,y])

class StaticElement():
    def __init__(self,element,pos):
        self.element = element
        self.pos = pos

class PositionalCard():
    def __init__(self,name,pos):
        self.name =name
        self.pos = pos

class ScreenProcessor():
    def __init__(self):
        self.staticElements = {}
        self.frameElements = {}
        self.cardElements = {}
        self.cards = []
        self.currentFrame = ""
        self.framePosition = [0,0]

    def positionFrames(self,pos):
        self.framePosition = pos

    def addFrame(self,name,element):
        self.frameElements[name] = element

    def addCard(self,name,element):
        self.cardElements[name] = element

    def setCard(self,name,pos):
        self.cards.append(PositionalCard(name,pos))

    def addElement(self,name,element,pos):
        self.staticElements[name] = StaticElement(element,pos)

    def getPositionInside(self,posCheck,pos0,pos1):
        if min(pos0[0],pos1[0])<posCheck[0]<max(pos0[0],pos1[0]):
            if min(pos0[1],pos1[1])<posCheck[1]<max(pos0[1],pos1[1]):
                return True
        return False

    def getFramePosition(self):
        frame = self.frameElements[self.currentFrame]
        positions = [[]] * 2
        positions[0] = self.framePosition
        positions[1] = [0] * 2
        positions[1][0] = frame.width+self.framePosition[0]
        positions[1][1] = frame.height+self.framePosition[1]
        return positions

    def getCardPosition(self,card):
        element = self.cardElements[card.name]
        positions = [[]] * 2
        positions[0] = card.pos
        positions[1] = [0] * 2
        positions[1][0] = element.width+card.pos[0]
        positions[1][1] = element.height+card.pos[1]
        return positions

    def getElementInPosition(self,pos):
        framePos = self.getFramePosition()
        if self.getPositionInside(pos,framePos[0],framePos[1]):
            return self.frameElements[self.currentFrame], self.currentFrame, framePos[0]
        for card in self.cards:
            cardPos = self.getCardPosition(card)
            if self.getPositionInside(pos,cardPos[0],cardPos[1]):
                return self.cardElements[card.name], card.name, cardPos[0]
        return False,"",[0,0]

    def changeFrame(self,name):
        if name in self.frameElements:
            self.currentFrame = name
        
    def render(self):
        self.frameElements[self.currentFrame].render()
        for i in self.staticElements:
            element = self.staticElements[i]
            element.element.render()
        for card in self.cards:
            element = self.cardElements[card.name]
            element.render()

    def blit(self,screen):
        screen.blit(self.frameElements[self.currentFrame].surface,self.framePosition)
        for i in self.staticElements:
            element = self.staticElements[i]
            screen.blit(element.element.surface,element.pos)
        for card in self.cards:
            element = self.cardElements[card.name]
            screen.blit(element.surface,card.pos)

class InputProcessor():
    def __init__(self):
        self.screen = ScreenProcessor()
        pass

    def addScreenProcessor(self,sp): 
        self.screen = sp

    def processEvent(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            print('processing button')
            element,name,pos = self.screen.getElementInPosition(event.pos)
            print(name)
            self.screen.changeFrame(name)


server = ThreadingSimpleServer(('0.0.0.0',8080), Handler)

if __name__ == '__main__':
    screen = pygame.display.set_mode(size)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    inputProcessor = InputProcessor()
    screenProcessor = ScreenProcessor()
    memberPresence = MemberPresence()

    inputProcessor.addScreenProcessor(screenProcessor)
    screenProcessor.positionFrames([460,30])

    theChat = Chat(400,840,33)
    screenProcessor.addElement('chat',theChat,[30,30])
    
    theClock = Clock(400,150)
    screenProcessor.addElement('clock',theClock,[30,900])

    helloFrame = HelloFrame(1430,728)
    screenProcessor.addFrame('hello',helloFrame)
    screenProcessor.changeFrame('hello')

    memberFrame = MemberFrame(1430,728,memberPresence)
    screenProcessor.addFrame('member',memberFrame)

    blankCard = Card(262,262)
    screenProcessor.addCard('hello',blankCard)
    screenProcessor.setCard('hello',[752,788])
    screenProcessor.setCard('hello',[1044,788])
    screenProcessor.setCard('hello',[1336,788])
    screenProcessor.setCard('hello',[1628,788])

    memberCard = PresenceCard(262,262,memberPresence)
    screenProcessor.addCard('member',memberCard)
    screenProcessor.setCard('member',[460,788])

    while not done:
        clock.tick(10)
        for event in pygame.event.get():
            inputProcessor.processEvent(event)
            if event.type == pygame.QUIT:
                done = True
        screen.fill((70,70,70))
        screenProcessor.render()
        screenProcessor.blit(screen)
        pygame.display.flip()
    server.shutdown()
    pygame.quit()
