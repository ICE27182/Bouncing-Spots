#Bouncing spots v1.1 10/14/2022

#Functions
import math,time,threading,msvcrt,random,os
from coordinate_printing_2_4 import draw_c


def sin(theta):    return math.sin(theta*math.pi/180)
def cos(theta):    return math.cos(theta*math.pi/180)
def Int(val):    return int(round(val,0))
def posi(val):
    if val >= 0:
        return val
    else: return 0
def angle(theta,max=180,min=-180):
    '''To ensure that the theta is in the right range.'''
    while theta > max:
        theta -= 360
    while theta < min:
        theta += 360
    return theta

def coordinate_init():
    coordinate = {}    # {y:{x:color}}
    coordinate[frame[1]+2] = {x:370 for x in range(0,frame[0]+3)}
    coordinate[0] = coordinate[frame[1]+2]
    for y in range(frame[1]+1,0,-1):
        coordinate[y] = {0:370, frame[0]+2:370}
    return coordinate

def control():
    global space_gl,tp_gl,v_gl,p_gl,l_gl,boom_gl
    p_gl,l_gl,boom_gl = False,False,False
    while True:
        c = msvcrt.getwch()
        if c == 'w':
            if space_gl == '  ':
                space_gl = '\033[47m  \033[0m'
            else:   space_gl = '  '
        elif c == 't':
            tp_gl = True
        elif c == 'p':
            tp_gl = False
        elif c == 'Q':
            v_gl = 0
        elif c == 'n':
            v_gl = -1
        elif c == 'y':
            v_gl = 1
        elif c == 'P':
            p_gl = not p_gl
        elif c == '+':
            v_gl = 3
        elif c == '-':
            v_gl = -2
        elif c == 'l':
            l_gl = not l_gl
        elif c == 'b':
            boom_gl = not boom_gl

class Ball:
    def __init__(self):
        self.speed = -1
        while self.speed < 0 or self.speed > 2:
            self.speed = random.normalvariate(1,0.8)
        self.theta = random.randint(-180,180)
        self.ball = [random.randint(1,frame[0]),random.randint(1,frame[1]),random.randint(30,37)*10+random.randint(0,1)]
        self.life = 10
    def biu(self):
        #Ball's moving
        self.ball[0] += cos(self.theta)*self.speed
        self.ball[1] += sin(self.theta)*self.speed

        #Bouncing on the walls
        #Left, Right, Top
        for n in (1,2):
            if self.ball[0] < 0:
                self.ball[0] = 0
                self.theta = 180-self.theta
                if random.randint(0,10) <= 3:self.theta,self.ball[2] = random.randint(-180,180),random.randint(30,37)*10+random.randint(0,1)
            elif self.ball[0] > frame[0]:
                self.ball[0] = frame[0]
                self.theta = 180-self.theta
                if random.randint(0,10) <= 3:self.theta,self.ball[2] = random.randint(-180,180),random.randint(30,37)*10+random.randint(0,1)
            elif self.ball[1] > frame[1]:
                self.ball[1] = frame[1]
                self.theta = -self.theta
                if random.randint(0,10) <= 3:self.theta,self.ball[2] = random.randint(-180,180),random.randint(30,37)*10+random.randint(0,1)
            elif self.ball[1] < 0:
                self.ball[1] = 0
                self.theta = -self.theta
                if random.randint(0,10) <= 3:self.theta,self.ball[2] = random.randint(-180,180),random.randint(30,37)*10+random.randint(0,1)

        coordinate[Int(self.ball[1])].update({Int(self.ball[0]):self.ball[2],Int(self.ball[0])+1:self.ball[2]})
        coordinate[Int(self.ball[1]+1)].update({Int(self.ball[0]):self.ball[2],Int(self.ball[0])+1:self.ball[2]})

        if self.theta in (0,180,-180):
            self.theta = abs(angle(self.theta+1))

        return self.theta,self.ball[2],coordinate

    def tp(self):
        if random.randint(0,1_000) <= 5:
            self.ball[0],self.ball[1] = random.randint(1,frame[0]),random.randint(1,frame[1])
            if random.randint(0,1_000) <= 200:
                self.ball[2] = random.randint(30,37)*10+random.randint(0,2)
        return self.ball[0],self.ball[1],self.ball[2]


#Default Arguments
frame = (200,100)
coordinate = coordinate_init()
tp_gl = True
v_gl = 9
space_gl = '  '

balls = []
for n in range(0,25):
    balls.append(Ball())

E = threading.Thread(target=control,daemon=True)
E.start()
while 1:
    st = time.time()
    while p_gl:pass

    if random.randint(1,8) == 1 and len(balls) > 1 or random.randint(1,4) == 1 and len(balls) > 75:
        i = random.randint(0,len(balls)-1)
        if balls[i].life < 0:
            del balls[i]
    if random.randint(1,8) == 1 and len(balls) <= 75 or random.randint(1,4) == 1 and len(balls) in range(1,5):
        balls.append(Ball())
    if random.randint(1,2048) == 1 and boom_gl:
        balls.clear()
    elif random.randint(1,2048) == 1 and boom_gl:
        for n in range(0,75):
            balls.append(Ball())
    
    if not l_gl:
        coordinate = coordinate_init()
    
    for ball in (balls):
        ball.theta,ball.ball[2],coordinate = ball.biu()
        ball.life -= 1
        if tp_gl:
            ball.ball[0],ball.ball[1],ball.ball[2] = ball.tp()

    print('\033[F'*(frame[1]+6),end='')
    draw_c(coordinate,y_axis=False,x_limit=True,space=space_gl)
    print('\033[F',end='')
    print(f'\033[47;30;2m{len(balls):4}\t\t{str(boom_gl):5}\033[0m')

    if v_gl == 0:
        break
    elif v_gl == -1:
        balls.clear()
        v_gl = 9
    elif v_gl == 1:
        for n in range(0,75-len(balls)+1):
            balls.append(Ball())
        v_gl = 9
    elif v_gl == 3:
        for n in range(0,5):
            balls.append(Ball())
        v_gl = 9
    elif v_gl == -2:
        for n in range(4,-1,-1):
            try:   del balls[n]
            except: pass
        v_gl = 9
            

    time.sleep(posi(1/240-(time.time()-st)))
os.system('cls')