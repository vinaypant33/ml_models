import pygame
import random
import math
import sys
import time

WIDTH, HEIGHT = 600, 400
CELL = 20
GRID_W, GRID_H = WIDTH // CELL, HEIGHT // CELL
AGENT_COLOR = (255,255,255)
GOAL_COLOR = (0,0,0)
BG = (30,30,30)
TEXT = (240,240,240)
RADIUS = CELL//2 - 2

ACTIONS = [(0,0),(0,-1),(0,1),(-1,0),(1,0)]

class Env:
    def __init__(self):
        self.reset()

    def rand_cell(self):
        return random.randrange(GRID_W), random.randrange(GRID_H)

    def reset(self):
        self.ax, self.ay = self.rand_cell()
        self.gx, self.gy = self.rand_cell()
        while (self.ax,self.ay)==(self.gx,self.gy):
            self.gx,self.gy = self.rand_cell()
        self.steps = 0
        return (self.ax,self.ay,self.gx,self.gy)

    def step(self, action_idx):
        dx,dy = ACTIONS[action_idx]
        nx = max(0, min(GRID_W-1, self.ax+dx))
        ny = max(0, min(GRID_H-1, self.ay+dy))
        boundary_pen = -0.05 if (nx==0 and dx<0) or (nx==GRID_W-1 and dx>0) or (ny==0 and dy<0) or (ny==GRID_H-1 and dy>0) else 0.0
        self.ax, self.ay = nx, ny
        self.steps += 1
        done = (self.ax,self.ay)==(self.gx,self.gy)
        reward = 1.0 if done else -0.01 + boundary_pen
        s_next = (self.ax,self.ay,self.gx,self.gy)
        if done:
            self.gx,self.gy = self.rand_cell()
            while (self.ax,self.ay)==(self.gx,self.gy):
                self.gx,self.gy = self.rand_cell()
        return s_next, reward, done

    def render(self, screen):
        axp, ayp = self.ax*CELL + CELL//2, self.ay*CELL + CELL//2
        gxp, gyp = self.gx*CELL + CELL//2, self.gy*CELL + CELL//2
        pygame.draw.circle(screen, GOAL_COLOR, (gxp,gyp), RADIUS)
        pygame.draw.circle(screen, AGENT_COLOR, (axp,ayp), RADIUS)

class QAgent:
    def __init__(self, alpha=0.3, gamma=0.95, eps_start=0.9, eps_end=0.01, eps_decay=0.9995, seed=7):
        random.seed(seed)
        self.alpha=alpha
        self.gamma=gamma
        self.eps=eps_start
        self.eps_end=eps_end
        self.eps_decay=eps_decay
        self.Q={}

    def getQ(self, s):
        if s not in self.Q:
            self.Q[s]=[0.0]*len(ACTIONS)
        return self.Q[s]

    def act(self, s, greedy=False):
        q = self.getQ(s)
        if (not greedy) and random.random()<self.eps:
            return random.randrange(len(ACTIONS))
        m = max(q)
        idxs = [i for i,v in enumerate(q) if v==m]
        return random.choice(idxs)

    def update(self, s,a,r,sn,done):
        q = self.getQ(s)
        qn = self.getQ(sn)
        target = r if done else r + self.gamma*max(qn)
        q[a] += self.alpha*(target - q[a])

    def decay(self):
        self.eps = max(self.eps_end, self.eps*self.eps_decay)

def draw_grid(screen):
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, (50,50,50), (x,0), (x,HEIGHT))
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(screen, (50,50,50), (0,y), (WIDTH,y))

def text_blit(screen, font, lines, x, y):
    oy=0
    for line in lines:
        surf = font.render(line, True, TEXT)
        screen.blit(surf, (x, y+oy))
        oy += surf.get_height()+2

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pygame RL: White ball catches Black ball")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 22)

    env = Env()
    agent = QAgent()

    state = (env.ax,env.ay,env.gx,env.gy)
    total_reward = 0.0
    episode_return = 0.0
    episode_steps = 0
    episodes = 0
    catches = 0
    running = True
    training = True
    greedy_demo = False
    max_steps_per_episode = 200
    steps_this_episode = 0
    recent_returns = []
    train_steps_per_frame = 200

    while running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    running=False
                elif event.key==pygame.K_t:
                    training = not training
                    greedy_demo = False
                elif event.key==pygame.K_g:
                    greedy_demo = True
                    training = False
                elif event.key==pygame.K_r:
                    env.reset()
                    state = (env.ax,env.ay,env.gx,env.gy)
                    episode_return=0.0
                    episode_steps=0
                    steps_this_episode=0

        if training:
            for _ in range(train_steps_per_frame):
                a = agent.act(state, greedy=False)
                sn, r, done = env.step(a)
                agent.update(state,a,r,sn,done)
                agent.decay()
                episode_return += r
                episode_steps += 1
                steps_this_episode += 1
                state = sn
                if done or steps_this_episode>=max_steps_per_episode:
                    episodes += 1
                    if done: catches += 1
                    recent_returns.append(episode_return)
                    if len(recent_returns)>50:
                        recent_returns.pop(0)
                    env.reset()
                    state = (env.ax,env.ay,env.gx,env.gy)
                    episode_return=0.0
                    episode_steps=0
                    steps_this_episode=0
        else:
            a = agent.act(state, greedy=greedy_demo)
            sn, r, done = env.step(a)
            episode_return += r
            episode_steps += 1
            steps_this_episode += 1
            state = sn
            if done or steps_this_episode>=max_steps_per_episode:
                episodes += 1
                if done: catches += 1
                recent_returns.append(episode_return)
                if len(recent_returns)>50:
                    recent_returns.pop(0)
                env.reset()
                state = (env.ax,env.ay,env.gx,env.gy)
                episode_return=0.0
                episode_steps=0
                steps_this_episode=0

        screen.fill(BG)
        draw_grid(screen)
        env.render(screen)

        avg_ret = sum(recent_returns)/len(recent_returns) if recent_returns else 0.0
        lines = [
            f"Mode: {'TRAIN' if training else ('GREEDY' if greedy_demo else 'EPS-GREEDY')}",
            f"Episodes: {episodes}   Catches: {catches}",
            f"Epsilon: {agent.eps:.3f}",
            f"Return(ep): {episode_return:.3f}   Avg(50): {avg_ret:.3f}",
            f"Steps(ep): {steps_this_episode}",
            "Keys: T=train  G=greedy  R=reset  ESC=quit"
        ]
        text_blit(screen, font, lines, 10, 10)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__=="__main__":
    main()
