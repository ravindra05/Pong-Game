from pygame.locals import *
import random
import sys
import time
import pygame as pg
import numpy as np


start = time.time()


FPS = 30
fpsClock = pg.time.Clock()


pg.init()


window = pg.display.set_mode((800,600))
pg.display.set_caption('Pong-Game')


Qa = 0
Left = 400
Top = 570
Width = 100
Height = 20


BLACK = ( 0, 0, 0)
WHITE = ( 255, 255, 255)
GREEN = ( 0, 255, 0)



rct = pg.Rect(Left,Top,Width,Height)


action = 2


storage = {}

jumpX = 6
jumpY = 8


Q = np.zeros([2500,3])


cenX = 10
cenY = 50
radius = 10

score = 0
missed = 0
reward = 0

font = pg.font.Font(None,30)


lr =  0.7
y = 0.5
i = 0


def calculate_score(rect, circle):
    if rect.left <= circle.circleX <= rect.right:
        return 1
    else:
        return -1


def newXforCircle(radius):
    newx = 100 - radius
    multiplier = float(random.randint(1, 8))
    newx *= multiplier
    return newx

class State:
    def __init__(self, rect, circle):
        self.rect = rect
        self.circle = circle

class Circle:
    def __init__(self, circleX, circleY):
        self.circleX = circleX
        self.circleY = circleY

def convert(s):
    y = int(s.circle.circleY)
    x = int(s.circle.circleX)
    z = int(s.rect.left)
    n = float(str(x)+str(z))
    #print(str(x)+' '+str(y)+' '+str(x)+str(y)+str(z)+'  '+str(n))
    if n in storage:
        #print ('R  '+str(n))
        return storage[n]
    else:
        if len(storage):
            maximum = max(storage, key=storage.get)
            storage[n] = storage[maximum] + 1
        else:
            storage[n] = 1
    return storage[n]



def action(s):
    return np.argmax(Q[convert(s), :])

def afteraction(s, act):
    rct = None

    if act == 2:
        if s.rect.right + 100 > 800:
            rct = s.rect
        else:
            rct = pg.Rect(s.rect.left + 100, s.rect.top, s.rect.width,
                          s.rect.height)
    elif act == 1:
        if s.rect.left - 100 < 0:
            rct = s.rect
        else:
            rct = pg.Rect(s.rect.left - 100, s.rect.top, s.rect.width,
                          s.rect.height)  # Rect(left, top, width, height)

    else:  # action is 0, means stay where it is
        rct = s.rect
    X = s.circle.circleX + jumpX
    Y = s.circle.circleY + jumpY
    print (str(X)+'  '+str(Y))
    newCircle = Circle(X, Y)

    return State(rct, newCircle)


def newRect(rect, act):
    if act == 2:
        if rect.right + 100 > 800:
            return rect
        else:
            return pg.Rect(rect.left + 100, rect.top, rect.width, rect.height)
    elif act == 1:  # action is left
        if rect.left - 100 < 0:
            return rect
        else:
            return pg.Rect(rect.left - 100, rect.top, rect.width, rect.height)
    else:
        return rect


while True:
    for event in pg.event.get():
        if event.type == QUIT:
            np.savetxt('test.txt', Q)
            pg.quit()
            sys.exit()
    # RGB values for ball after collision
    COL = [(255,255,0),(255,215,0),(238,221,130),(218,165,32),(184,134,11),(208,32,144),(238,130,238),(221,160,221),
           (218,112,214),(186,85,211),(153,50,204),(148,0,211),(138,43,226),(173,255,47),(50,205,50),(154,205,50),
           (34,139,34),(107,142,35),(189,183,107),(240,230,140)]
    window.fill((255,255,255))

    if cenY >= 590 - Height - radius:
        reward = calculate_score(rct, Circle(cenX, cenY))
        if reward == -1:
            cenX = newXforCircle(radius)
            cenY = 50
        else:
            Qa = COL[random.randint(0,19)]
            jumpY *= -1
            cenY += jumpY
    elif cenY < 50 and i!=0:
        cenY += jumpY
        jumpY = abs(jumpY)

    else:
        cenY+=jumpY

    if cenX >= (800 - radius):
        jumpX *= -1
        cenX += jumpX
    elif cenX <= 2*radius and i!=0:
        cenX += jumpX
        jumpX = abs(jumpX)
    else:
        cenX += jumpX
        print('b')
    print (str(cenX))
    print('X: '+str(jumpX)+'  Y: '+str(jumpY))


    s = State(rct, Circle(cenX, cenY))
    act = action(s)
    r0 = calculate_score(s.rect, s.circle)


    s1 = afteraction(s, act)
    actx = action(s1)


    Q[convert(s), act] += lr*(r0 + y * np.max(Q[convert(s1), :]) - Q[convert(s), act])


    rct = newRect(s.rect, act)
    pg.draw.circle(window, Qa, (int(cenX),int(cenY)),radius)
    pg.draw.rect(window, GREEN, rct)

    if reward == 1:
        score += reward
    else:
        missed += reward
    reward = 0


    LR = '%.2f' % (abs(score+reward)/(1+abs(missed)+score)*100)
    text = font.render('Score: ' + str(score), True, (243, 160, 90))
    text1 = font.render('Penalty: ' + str(missed), True, (125, 157, 207))
    text2 = font.render('LR :' + str(LR), True, (0, 255, 20))
    window.blit(text, (670, 10))  # render score
    window.blit(text1, (10, 10))  # render missed
    window.blit(text2, (320, 10))

    pg.display.update()  # update display
    fpsClock.tick(FPS)
    i = 1