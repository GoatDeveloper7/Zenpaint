"""
Programmed by Randy Graham Junior.
ZenPaint, Just you and the colors.
"""
import pygame
import sys
import math
import json

with open("config.json", "r") as f:
    jdata = json.loads(f.read())

SCREENSIZE = jdata["SCREENSIZE"]

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode(SCREENSIZE)
TEXT = pygame.font.Font('freesansbold.ttf',30)

pygame.display.set_caption('ZenPaint v0.01')

def percentPos(x, y):
    return SCREENSIZE[0] * (x/100), SCREENSIZE[1] * (y/100)

class button(object):
    def __init__(self, posx, posy, sx, sy, text, color, highlight):
        self.posx = posx
        self.posy = posy
        self.color = color
        self.highlight = highlight
        self.sx = sx
        self.sy = sy
        self.text = text
        self.focused = False
        self.surf = pygame.Surface((sx, sy))
        temp = TEXT.render(text,True,(0,0,0))
        self.text = pygame.transform.scale(temp, (self.sx, self.sy))

    def show(self, dest):
        to_render = pygame.Surface((self.sx, self.sy))
        if self.focused:
            self.surf.fill(self.highlight)
        else:
            self.surf.fill(self.color)
        to_render.blit(self.surf, (0,0))
        to_render.blit(self.text, (0,0))
        dest.blit(to_render, (self.posx, self.posy))

    def test(self, pos):
        rect = pygame.Rect(self.posx, self.posy, self.sx, self.sy)
        if rect.collidepoint(pos[0], pos[1]):
            self.focused = True
            return True
        else:
            self.focused = False
            return False

class canvas(object):
    def __init__(self, sx, sy):
        self.sx = sx
        self.sy = sy
        self.surf = pygame.Surface((sx, sy))
        self.surf.fill((0,0,0))

    def update(self, posx, posy, color, brush_size):
        for x in range(0, brush_size):
            for y in range(0, brush_size):
                self.surf.set_at((int(posx-(brush_size/2)+x),int(posy-(brush_size/2)+y)), color)


    def show(self, surf, cam_rel):
        surf.blit(self.surf, (cam_rel[0], cam_rel[1]))


im = canvas(jdata["CANVASSIZE"][0], jdata["CANVASSIZE"][1])

#_-_ Main Game Loop _-_
cam_pos = [SCREENSIZE[0]/2, SCREENSIZE[1]/2]
cam_pos_const = [SCREENSIZE[0]/2, SCREENSIZE[1]/2]

c_color = [255,255,255]
b_color = (25,25,25)
b_size = 5
min_zoom = 100
max_zoom = 1000

ui = False

delay = 0

mbposx, mbposy = percentPos(1,1)
SizeUp = button(mbposx, mbposy, 90, 30, " Brush Size + ", (100,100,100), (0,255,0))

mbposx, mbposy = percentPos(1,6)
SizeDown = button(mbposx, mbposy, 90, 30, " Brush Size - ", (100,100,100), (0,255,0))

mbposx, mbposy = percentPos(20,1)
R = button(mbposx, mbposy, 80, 40, " R ", (255,0,0), (100,100,100))

mbposx, mbposy = percentPos(40,1)
G = button(mbposx, mbposy, 80, 40, " G ", (0,255,0), (100,100,100))

mbposx, mbposy = percentPos(60,1)
B = button(mbposx, mbposy, 80, 40, " B ", (0,0,255), (100,100,100))

mbposx, mbposy = percentPos(1,15)
Save = button(mbposx, mbposy, 100, 40, " Save ", (100,0,0), (100,100,100))

mbposx, mbposy = percentPos(1,92)
temp = TEXT.render(f"color R:{c_color[0]} G:{c_color[1]} B:{c_color[2]}, Brush Size {b_size}",True,(0,0,0))
info = pygame.transform.scale(temp, (SCREENSIZE[0]-150, 50))

timer = pygame.time.Clock()

running = True
while running:
    delta = timer.tick()
    if delta > 0:
        fps = 1/(delta/1000) 
    else:
        fps = 0

    delay -= 1
    ui = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    mouse_pos = pygame.mouse.get_pos()
    mouse_left = pygame.mouse.get_pressed()[0]
    mouse_right = pygame.mouse.get_pressed()[2]

    keys = pygame.key.get_pressed()

    #""" Screen panning by moving mouse to edge of screen
    if keys[pygame.K_a]:
        cam_pos[0] -= 1
    if keys[pygame.K_d]:
        cam_pos[0] += 1
    if keys[pygame.K_w]:
        cam_pos[1] -= 1
    if keys[pygame.K_s]:
        cam_pos[1] += 1

    if SizeUp.test(mouse_pos) and mouse_left and delay < 0:
        b_size += 1
        ui = True
        
    if SizeDown.test(mouse_pos) and mouse_left and delay < 0:
        b_size -= 1
        ui = True

    if R.test(mouse_pos) and mouse_left and delay < 0:
        ui = True
        c_color[0] += 5
        if c_color[0] > 255:
            c_color[0] = 0

    if G.test(mouse_pos) and mouse_left and delay < 0:
        ui = True
        c_color[1] += 5
        if c_color[1] > 255:
            c_color[1] = 0

    if B.test(mouse_pos) and mouse_left and delay < 0:
        ui = True
        c_color[2] += 5
        if c_color[2] > 255:
            c_color[2] = 0

    if Save.test(mouse_pos) and mouse_left and delay < 0:
        ui = True
        pygame.image.save(im.surf, "MyZenDrawing.png")

    cam_rel = (cam_pos_const[0] - cam_pos[0], cam_pos_const[1] - cam_pos[1])

    #print(mouse_pos)

    if not ui:
        if mouse_right:
            im.update(mouse_pos[0]-cam_rel[0], mouse_pos[1]-cam_rel[1], (0,0,0), b_size*2)

        if mouse_left:
            im.update(mouse_pos[0]-cam_rel[0], mouse_pos[1]-cam_rel[1], c_color, b_size)

    screen.fill(b_color)

    im.show(screen, cam_rel)

    if ui:
        delay = 20
        temp = TEXT.render(f"color R:{c_color[0]} G:{c_color[1]} B:{c_color[2]}, Brush Size {b_size}",True,(0,0,0))
        info = pygame.transform.scale(temp, (SCREENSIZE[0]-150, 50))
    
    info_widgit = pygame.Surface((20,20))
    info_widgit.fill(c_color)
    dummyx, dummyy = percentPos(80,1)
    screen.blit(info_widgit, (dummyx, dummyy))

    t = TEXT.render(f"{int(fps)}", True, (0,0,255))
    px, py = percentPos(90,1)
    screen.blit(t, (px,py))

    SizeUp.show(screen)
    SizeDown.show(screen)
    R.show(screen)
    G.show(screen)
    B.show(screen)
    Save.show(screen)
    screen.blit(info, (mbposx, mbposy))

    pygame.display.flip()
    
