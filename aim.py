import pygame, random, sys, datetime, os, ctypes

# --- 1. WINDOWS DPI FIX ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

pygame.init()

# --- 2. DYNAMIC SCALING LOGIC ---
info = pygame.display.Info()
CURRENT_W = info.current_w
SCALE = CURRENT_W / 1920

# --- 3. VALORANT BASIS CONSTANTS ---
MY_DPI = 1600
VAL_YAW = 0.07065  # Precise Valorant Yaw
VAL_FOV = 103      # Standard Valorant FOV

WIDTH = int(1200 * SCALE)
HEIGHT = int(950 * SCALE)
FPS = 0 # Unlocked for M4 Mac smoothness
ROUND_TIME = 60

# --- Colors & Lists ---
COLORS = [(0, 255, 255), (0, 255, 0), (255, 0, 255), (255, 255, 255), (255, 255, 0)]
COLOR_NAMES = ["Cyan", "Green", "Pink", "White", "Yellow"]
XHAIR_TYPES = ["Dot", "Cross", "T-Shape"]

# --- SENSITIVITY CONVERTER ---
def get_cm_360(sens):
    # Calculates physical distance for a 360-degree turn
    if sens <= 0: return 0
    return (360 * 2.54) / (MY_DPI * sens * VAL_YAW)

def get_in_360(sens):
    # Calculates inches for a 360-degree turn
    return get_cm_360(sens) / 2.54

# --- FILE HANDLERS ---
def save_settings(sens, color, x_type, size, speed):
    with open("config.txt", "w") as f:
        f.write(f"{sens}\n{color}\n{x_type}\n{size}\n{speed}")

def load_settings():
    if os.path.exists("config.txt"):
        try:
            with open("config.txt", "r") as f:
                lines = f.readlines()
                return float(lines[0]), int(lines[1]), int(lines[2]), int(lines[3]), float(lines[4])
        except: pass
    return 0.125, 0, 0, 20, 1.05

def save_stats(mode_name, shots, hits, acc, sens, size, speed):
    timestamp = datetime.datetime.now().strftime("%m/%d %H:%M")
    info = f"[{timestamp}] {mode_name:7} | {int(hits)}/{shots} Hits | {acc:.1f}% | Sens: {sens} | Size: {size}"
    if mode_name == "Strafe": info += f" | Spd: {speed}"
    with open("aim_stats.txt", "a") as f: f.write(info + "\n")

def draw_xhair(surf, x, y, color, t_idx):
    thick = max(1, int(2 * SCALE))
    length = int(8 * SCALE)
    dot_rad = int(3 * SCALE)
    if t_idx == 0: pygame.draw.circle(surf, color, (int(x), int(y)), dot_rad)
    elif t_idx == 1:
        pygame.draw.line(surf, color, (x-length, y), (x+length, y), thick)
        pygame.draw.line(surf, color, (x, y-length), (x, y+length), thick)
    elif t_idx == 2:
        pygame.draw.line(surf, color, (x-length, y), (x+length, y), thick)
        pygame.draw.line(surf, color, (x, y), (x, y+length), thick)

def run():
    val_sens, col_idx, type_idx, t_size, s_speed = load_settings()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    font = pygame.font.SysFont("Verdana", int(14 * SCALE))
    l_font = pygame.font.SysFont("Verdana", int(40 * SCALE))
    m_font = pygame.font.SysFont("Verdana", int(22 * SCALE))
    
    clock = pygame.time.Clock()
    state, mode, score, shots, hits = "MENU", 0, 0, 0, 0
    cx, cy, targets, start_t, s_dir, s_timer = WIDTH//2, HEIGHT//2, [], 0, 1, 0
    history_view_mode = 1 

    while True:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.1) 

        # Pixels per "count" based on Valorant logic
        px_per_cnt = (val_sens * VAL_YAW * WIDTH) / VAL_FOV
        screen.fill((10, 10, 15))
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT: 
                save_settings(val_sens, col_idx, type_idx, t_size, s_speed)
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    if state == "GAME": state = "MENU"; pygame.mouse.set_visible(True)
                    else: save_settings(val_sens, col_idx, type_idx, t_size, s_speed); pygame.quit(); sys.exit()
                
                if state != "GAME":
                    if e.key == pygame.K_s: state = "SETTINGS"
                    if e.key == pygame.K_h: state = "HISTORY"
                    if e.key == pygame.K_m: state = "MENU"
                
                if state == "HISTORY" and e.unicode in "1234":
                    history_view_mode = int(e.unicode)
                elif e.unicode in "1234":
                    mode, score, shots, hits, start_t, state = int(e.unicode), 0, 0, 0, pygame.time.get_ticks(), "GAME"
                    targets = []
                    if mode == 1: [targets.append([random.randint(int(200*SCALE), int(1000*SCALE)), random.randint(int(200*SCALE), int(700*SCALE))]) for _ in range(3)]
                    elif mode == 2: targets.append([random.randint(int(200*SCALE), int(1000*SCALE)), HEIGHT//2])
                    elif mode in [3, 4]:
                        bx, by, v = random.randint(int(300*SCALE), int(900*SCALE)), random.randint(int(300*SCALE), int(600*SCALE)), (int(70*SCALE) if mode==3 else int(30*SCALE))
                        [targets.append([bx+random.randint(-v, v), by+random.randint(-v, v)]) for _ in range(5 if mode==3 else 4)]
                    pygame.mouse.set_visible(False); pygame.event.set_grab(True)
                
                if state == "SETTINGS":
                    if e.key == pygame.K_g: val_sens = round(val_sens + 0.005, 4)
                    if e.key == pygame.K_j: val_sens = round(max(0.001, val_sens - 0.005), 4)
                    if e.key == pygame.K_c: col_idx = (col_idx + 1) % len(COLORS)
                    if e.key == pygame.K_t: type_idx = (type_idx + 1) % len(XHAIR_TYPES)
                    if e.key == pygame.K_d: t_size = min(50, t_size + 2)
                    if e.key == pygame.K_a: t_size = max(4, t_size - 2)
                    if e.key == pygame.K_w: s_speed = round(s_speed + 0.1, 2)
                    if e.key == pygame.K_q: s_speed = round(max(0.1, s_speed - 0.1), 2)
                    save_settings(val_sens, col_idx, type_idx, t_size, s_speed)

        if state == "GAME":
            rem = max(0, ROUND_TIME - (pygame.time.get_ticks() - start_t) / 1000)
            if rem <= 0:
                save_stats({1:"Grid",2:"Strafe",3:"Cluster",4:"Micro"}[mode], shots, hits, (hits/shots*100 if shots>0 else 0), val_sens, t_size, s_speed)
                state = "HISTORY"; history_view_mode = mode; pygame.mouse.set_visible(True); pygame.event.set_grab(False)
            
            dx, dy = pygame.mouse.get_rel()
            cx, cy = max(0, min(WIDTH, cx + dx * px_per_cnt)), max(0, min(HEIGHT, cy + dy * px_per_cnt))
            
            if mode == 2 and targets:
                s_timer -= dt
                if s_timer <= 0: s_dir *= -1; s_timer = random.uniform(0.4, 1.1) 
                targets[0][0] += s_dir * (s_speed * 450 * SCALE) * dt
                if targets[0][0] < 150*SCALE: s_dir = 1
                elif targets[0][0] > 1050*SCALE: s_dir = -1
            
            for t in targets:
                rad = (t_size * SCALE) if mode <= 2 else (t_size * SCALE * 0.6 if mode == 3 else t_size * SCALE * 0.4)
                pygame.draw.circle(screen, (255, 60, 60), (int(t[0]), int(t[1])), int(rad))
            
            draw_xhair(screen, cx, cy, COLORS[col_idx], type_idx)
            # HUD with FPS and Sens Info
            sens_text = f"VAL SENS: {val_sens} | {get_in_360(val_sens):.1f} in/360 | FPS: {int(clock.get_fps())}"
            screen.blit(font.render(sens_text, True, (255, 255, 255)), (20, 20))

        elif state == "SETTINGS":
            screen.blit(l_font.render("SETTINGS", True, (0, 255, 200)), (100*SCALE, 80*SCALE))
            screen.blit(font.render(f"VALORANT SENS: {val_sens} (G/J)", True, (255,255,255)), (100*SCALE, 180*SCALE))
            screen.blit(font.render(f"PHYSICAL: {get_cm_360(val_sens):.2f} cm/360 ({get_in_360(val_sens):.2f} in/360)", True, (150,150,150)), (100*SCALE, 210*SCALE))
            screen.blit(font.render(f"TARGET SIZE: {t_size} (A/D)", True, (255,255,255)), (100*SCALE, 260*SCALE))
            
            pygame.draw.circle(screen, (255, 60, 60), (int(600*SCALE), int(280*SCALE)), int(t_size*SCALE))
            draw_xhair(screen, 600*SCALE, 280*SCALE, COLORS[col_idx], type_idx)
            screen.blit(font.render("M: Menu", True, (255,255,0)), (100*SCALE, 450*SCALE))

        elif state == "MENU":
            screen.blit(l_font.render("AIM DOTS", True, (255, 255, 255)), (WIDTH//2 - int(180*SCALE), 100*SCALE))
            for i, txt in enumerate(["1. Gridshot", "2. Dynamic Strafe", "3. Cluster", "4. Micro"]):
                screen.blit(m_font.render(txt, True, (200, 200, 200)), (WIDTH//2 - int(120*SCALE), (220*SCALE) + (i*50*SCALE)))
            screen.blit(font.render("S: Settings | H: History | ESC: Quit", True, (0, 255, 200)), (WIDTH//2 - int(140*SCALE), 500*SCALE))

        pygame.display.flip()

if __name__ == "__main__":
    run()