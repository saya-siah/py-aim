import pygame, random, sys, datetime, os, ctypes

# --- 1. WINDOWS DPI FIX (Forces PC to use real pixels) ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

pygame.init()

# --- 2. DYNAMIC SCALING LOGIC ---
# We get the width of whatever monitor you are currently on.
info = pygame.display.Info()
CURRENT_W = info.current_w

# Use 1920 (your PC) as the "Base 1.0"
# On PC: 1920/1920 = 1.0 | On Mac: 2560/1920 = 1.33
SCALE = CURRENT_W / 1920

# --- 3. ADJUSTED INITIAL SETTINGS ---
MY_DPI = 1600
VAL_YAW, VAL_FOV = 0.07, 103

# Scale the window and targets relative to the screen density
WIDTH = int(1200 * SCALE)
HEIGHT = int(950 * SCALE)
FPS, ROUND_TIME = 144, 60

# --- Colors & Lists ---
COLORS = [(0, 255, 255), (0, 255, 0), (255, 0, 255), (255, 255, 255), (255, 255, 0)]
COLOR_NAMES = ["Cyan", "Green", "Pink", "White", "Yellow"]
XHAIR_TYPES = ["Dot", "Cross", "T-Shape"]

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
    # Scale crosshair thickness and length
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
    
    # Scale fonts so they aren't tiny on Mac
    font = pygame.font.SysFont("Verdana", int(14 * SCALE))
    l_font = pygame.font.SysFont("Verdana", int(40 * SCALE))
    m_font = pygame.font.SysFont("Verdana", int(22 * SCALE))
    
    clock = pygame.time.Clock()
    state, mode, score, shots, hits = "MENU", 0, 0, 0, 0
    cx, cy, targets, start_t, s_dir, s_timer = WIDTH//2, HEIGHT//2, [], 0, 1, 0
    history_view_mode = 1 

    while True:
        # px_per_cnt is now resolution-independent because it uses WIDTH which is scaled
        px_per_cnt = (val_sens * VAL_YAW * WIDTH) / VAL_FOV
        screen.fill((10, 10, 15))
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT: save_settings(val_sens, col_idx, type_idx, t_size, s_speed); pygame.quit(); sys.exit()
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
                    # Scale spawn areas
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

            if state == "GAME" and e.type == pygame.MOUSEBUTTONDOWN:
                shots += 1
                for t in targets[:]:
                    d = ((cx-t[0])**2 + (cy-t[1])**2)**0.5
                    # Target hit detection uses t_size scaled by SCALE
                    limit = (t_size * SCALE) if mode <= 2 else (t_size * SCALE * 0.6 if mode == 3 else t_size * SCALE * 0.4)
                    if d <= limit:
                        hits += 1; score += 1; targets.remove(t)
                        if mode == 1: targets.append([random.randint(int(200*SCALE), int(1000*SCALE)), random.randint(int(200*SCALE), int(700*SCALE))])
                        elif mode == 2: targets.append([random.randint(int(200*SCALE), int(1000*SCALE)), (HEIGHT//2) + random.randint(int(-25*SCALE), int(25*SCALE))])
                        elif mode in [3, 4] and not targets:
                            bx, by, v = random.randint(int(300*SCALE), int(900*SCALE)), random.randint(int(300*SCALE), int(600*SCALE)), (int(70*SCALE) if mode==3 else int(30*SCALE))
                            [targets.append([bx+random.randint(-v,v), by+random.randint(-v,v)]) for _ in range(4 if mode==4 else 5)]

        if state == "GAME":
            rem = max(0, ROUND_TIME - (pygame.time.get_ticks() - start_t) / 1000)
            if rem <= 0:
                save_stats({1:"Grid",2:"Strafe",3:"Cluster",4:"Micro"}[mode], shots, hits, (hits/shots*100 if shots>0 else 0), val_sens, t_size, s_speed)
                state = "HISTORY"; history_view_mode = mode; pygame.mouse.set_visible(True); pygame.event.set_grab(False)
            
            dx, dy = pygame.mouse.get_rel()
            cx, cy = max(0, min(WIDTH, cx + dx * px_per_cnt)), max(0, min(HEIGHT, cy + dy * px_per_cnt))
            
            if mode == 2 and targets:
                s_timer -= 1
                if s_timer <= 0: s_dir *= -1; s_timer = random.randint(40, 150)
                # Strafe speed multiplied by SCALE so physical movement speed matches
                targets[0][0] += s_dir * s_speed * SCALE
                if targets[0][0] < 150*SCALE or targets[0][0] > 1050*SCALE: s_dir *= -1
            
            for t in targets:
                rad = (t_size * SCALE) if mode <= 2 else (t_size * SCALE * 0.6 if mode == 3 else t_size * SCALE * 0.4)
                pygame.draw.circle(screen, (255, 60, 60), (int(t[0]), int(t[1])), int(rad))
            
            draw_xhair(screen, cx, cy, COLORS[col_idx], type_idx)
            screen.blit(font.render(f"TIME: {rem:.1f}s | SCORE: {int(score)}", True, (255, 255, 255)), (20, 20))

        elif state == "HISTORY":
            h_mode_name = {1:"Grid", 2:"Strafe", 3:"Cluster", 4:"Micro"}[history_view_mode]
            screen.blit(l_font.render(f"{h_mode_name.upper()} PROGRESS", True, (0, 255, 150)), (50*SCALE, 30*SCALE))
            
            history_data = []
            if os.path.exists("aim_stats.txt"):
                with open("aim_stats.txt", "r") as f:
                    all_lines = f.readlines()
                    filtered = [l for l in all_lines if h_mode_name in l][-15:]
                    for i, l in enumerate(filtered):
                        screen.blit(font.render(l.strip(), True, (180, 180, 180)), (50*SCALE, (100*SCALE) + (i*25*SCALE)))
                        try:
                            parts = l.split('|')
                            hits_val = int(parts[1].split('/')[0].strip())
                            history_data.append(hits_val)
                        except: pass

            # --- GRAPH SCALING ---
            g_x, g_y, g_w, g_h = 600*SCALE, 100*SCALE, 500*SCALE, 300*SCALE
            pygame.draw.rect(screen, (20, 20, 30), (g_x, g_y, g_w, g_h))
            pygame.draw.line(screen, (100, 100, 100), (g_x, g_y + g_h), (g_x + g_w, g_y + g_h), 2)
            pygame.draw.line(screen, (100, 100, 100), (g_x, g_y), (g_x, g_y + g_h), 2)

            if len(history_data) > 1:
                max_h = max(history_data) if max(history_data) > 0 else 1
                points = []
                for i, val in enumerate(history_data):
                    px = g_x + (i * (g_w / (len(history_data)-1)))
                    py = g_y + g_h - (val / (max_h * 1.2) * g_h)
                    points.append((px, py))
                pygame.draw.lines(screen, (0, 255, 255), False, points, 3)
                for p in points: pygame.draw.circle(screen, (255, 255, 255), (int(p[0]), int(p[1])), int(4*SCALE))

            screen.blit(font.render("Press 1-4 to switch Mode Graph | M: Menu", True, (255, 255, 0)), (50*SCALE, HEIGHT-(40*SCALE)))

        elif state == "SETTINGS":
            screen.blit(l_font.render("SETTINGS", True, (0, 255, 200)), (100*SCALE, 80*SCALE))
            screen.blit(font.render(f"SENSITIVITY: {val_sens} (G/J)", True, (255,255,255)), (100*SCALE, 180*SCALE))
            screen.blit(font.render(f"TARGET SIZE: {t_size} (A/D)", True, (255,255,255)), (100*SCALE, 230*SCALE))
            screen.blit(font.render(f"STRAFE SPEED: {s_speed} (Q/W)", True, (255,255,255)), (100*SCALE, 280*SCALE))
            screen.blit(font.render(f"COLOR: {COLOR_NAMES[col_idx]} (C) | TYPE: {XHAIR_TYPES[type_idx]} (T)", True, (255,255,255)), (100*SCALE, 330*SCALE))
            pygame.draw.rect(screen, (20, 20, 30), (500*SCALE, 180*SCALE, 200*SCALE, 200*SCALE))
            pygame.draw.circle(screen, (255, 60, 60), (int(600*SCALE), int(280*SCALE)), int(t_size*SCALE))
            draw_xhair(screen, 600*SCALE, 280*SCALE, COLORS[col_idx], type_idx)
            screen.blit(font.render("M: Menu", True, (255,255,0)), (100*SCALE, 450*SCALE))

        elif state == "MENU":
            screen.blit(l_font.render("AIM DOTS", True, (255, 255, 255)), (WIDTH//2 - int(180*SCALE), 100*SCALE))
            for i, txt in enumerate(["1. Gridshot", "2. Dynamic Strafe", "3. Cluster", "4. Micro"]):
                screen.blit(m_font.render(txt, True, (200, 200, 200)), (WIDTH//2 - int(120*SCALE), (220*SCALE) + (i*50*SCALE)))
            screen.blit(font.render("S: Settings | H: History | ESC: Quit", True, (0, 255, 200)), (WIDTH//2 - int(140*SCALE), 500*SCALE))

        pygame.display.flip(); clock.tick(FPS)

if __name__ == "__main__":
    run()