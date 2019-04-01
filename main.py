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
if jdata["FULLSCREEN"] == "True":
    screen = pygame.display.set_mode(SCREENSIZE, pygame.FULLSCREEN)
else:
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
        self.to_do = []
        self.actions = []
        self.temp_store = []
        self.surf = pygame.Surface((sx, sy))
        self.surf.fill((0,0,0))

    def update(self, posx, posy, color, brush_size):
        self.temp_store.append([posx, posy, brush_size])
        for x in range(0, brush_size):
            for y in range(0, brush_size):
                self.surf.set_at((int(posx-(brush_size/2)+x),int(posy-(brush_size/2)+y)), color)

    def fl(self, x,y,t,r):
        try:
            n = self.surf.get_at((x,y))[:3]
        except Exception:
            return
        if t == r:
            return
        if n[0] == t[0] and n[1] == t[1] and n[2] == t[2]:
            pass
        else:
            return
        self.surf.set_at((x,y), r)
        self.to_do.append((x+1,y,t,r))
        self.to_do.append((x-1,y,t,r))
        self.to_do.append((x,y+1,t,r))
        self.to_do.append((x,y-1,t,r))
        return

    def flood(self, posx, posy, color_t, color_r):
        posx = int(posx)
        posy = int(posy)
        self.to_do = []
        self.to_do.append((posx, posy, color_t, color_r))
        """
        Flood-fill (node, target-color, replacement-color):
        1. If target-color is equal to replacement-color, return.
        2. If the color of node is not equal to target-color, return.
        3. Set the color of node to replacement-color.
        4. Perform Flood-fill (one step to the south of node, target-color, replacement-color).
            Perform Flood-fill (one step to the north of node, target-color, replacement-color).
            Perform Flood-fill (one step to the west of node, target-color, replacement-color).
            Perform Flood-fill (one step to the east of node, target-color, replacement-color).
        5. Return.
        """
        
        while len(self.to_do) > 0:
            self.fl(self.to_do[0][0],self.to_do[0][1],self.to_do[0][2],self.to_do[0][3])
            del self.to_do[0]
            

    def update_no_undo(self, posx, posy, brush_size):
        for x in range(0, brush_size):
            for y in range(0, brush_size):
                self.surf.set_at((int(posx-(brush_size/2)+x),int(posy-(brush_size/2)+y)), (0,0,0))

    def add_temp(self):
        self.actions.append(self.temp_store)
        self.temp_store = []

    def show(self, surf, cam_rel):
        surf.blit(self.surf, (cam_rel[0], cam_rel[1]))

    def test(self, pos, cam_rel):
        rect = pygame.Rect(cam_rel[0], cam_rel[1], self.sx, self.sy)
        if rect.collidepoint(pos[0], pos[1]):
            return True
        else:
            return False


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

m_continuos = False
do_up = False
s_foc = False

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
    mouse_middle = pygame.mouse.get_pressed()[1]

    if mouse_left and not m_continuos:
        m_continuos = True

    if m_continuos and not mouse_left:
        m_continuos = False

    keys = pygame.key.get_pressed()

    #""" camera scroll
    if keys[pygame.K_a]:
        cam_pos[0] -= 1
    if keys[pygame.K_d]:
        cam_pos[0] += 1
    if keys[pygame.K_w]:
        cam_pos[1] -= 1
    if keys[pygame.K_s]:
        cam_pos[1] += 1
    if keys[pygame.K_z]: #UNDO (note, Is retarted.)s
        if len(im.actions) > 0 and delay < 0:
            delay = 20
            work = im.actions[len(im.actions)-1]
            im.actions.pop()
            for t in work:
                im.update_no_undo(t[0], t[1], t[2])
    if keys[pygame.K_ESCAPE]:
        pygame.quit()

    cam_rel = (cam_pos_const[0] - cam_pos[0], cam_pos_const[1] - cam_pos[1])

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

    #print(mouse_pos)

    if not ui:
        if mouse_right:
            im.update(mouse_pos[0]-cam_rel[0], mouse_pos[1]-cam_rel[1], (0,0,0), b_size*2)

        if mouse_left:
            im.update(mouse_pos[0]-cam_rel[0], mouse_pos[1]-cam_rel[1], c_color, b_size)
        
        if mouse_middle:
            ap = im.surf.get_at((int(mouse_pos[0]-cam_rel[0]), int(mouse_pos[1]-cam_rel[1])))
            im.flood(mouse_pos[0]-cam_rel[0], mouse_pos[1]-cam_rel[1], ap[:3], c_color)

    screen.fill(b_color)

    s_foc = im.test(mouse_pos, cam_rel)

    im.show(screen, cam_rel)

    if not m_continuos and do_up and s_foc:
        im.add_temp()

    if ui:
        delay = 20
        temp = TEXT.render(f"color R:{c_color[0]} G:{c_color[1]} B:{c_color[2]}, Brush Size {b_size}",True,(0,0,0))
        info = pygame.transform.scale(temp, (SCREENSIZE[0]-150, 50))
    
    info_widgit = pygame.Surface((20,20))
    info_widgit.fill(c_color)
    dummyx, dummyy = percentPos(80,1)
    screen.blit(info_widgit, (dummyx, dummyy))

    t = TEXT.render("{}".format(int(fps)), True, (0,0,255))
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
    if not m_continuos or delay > 0:
        do_up = False
    else:
        do_up = True
    
