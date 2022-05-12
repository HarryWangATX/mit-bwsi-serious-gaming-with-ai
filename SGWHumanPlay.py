import json
import uuid
import gym
import gym_sgw  # Required, don't remove!
import pygame as pg
from pygame.locals import *
import keyboard
from gym_sgw.envs.enums.Enums import Actions, Terrains, PlayTypes, MapProfiles, MapColors
from gym_sgw.envs.SGWEnv import SGW
import matplotlib
matplotlib.use("Agg")
import matplotlib.backends.backend_agg as agg
import matplotlib.pyplot as plt
import pylab
import sys
import os

class SGW_human:
    """
    Human play game variant.
    """
    def __init__(self, data_log_file='data_log.json', max_energy=50, map_file=None,
                 rand_prof=MapProfiles.custom_made, num_rows=25, num_cols=25, mode=1):
        self.ENV_NAME = 'SGW-v0'
        self.DATA_LOG_FILE_NAME = data_log_file
        self.GAME_ID = uuid.uuid4()
        self.env = None
        self.current_action = Actions.none
        self.max_energy = max_energy
        self.map_file = map_file
        self.rand_prof = rand_prof
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.mode = mode
        self.is_game_over = False
        self.turn = 0
        self.max_turn = 300  # to prevent endless loops and games
        self.cell_size = 30
        pg.init()
        self.game_screen = pg.display.set_mode((1470, 800))
        self.play_area = None
        self.info = {'turn_reward': 0, 'total_reward': 0, 'turn_energy_used': 0, 'total_energy_used': 0, 'total_energy_remaining': 50}
        self.game_score_data = {
            'zombies_squished': 0,
            'pedestrians_squished': 0,
            'injured_saved': 0,
            'injured_squished': 0
        }
        # Always do these actions upon start
        self.start_screen()
        self._setup()

    def _setup(self):
        # Game parameters
        self.env = gym.make(self.ENV_NAME)
        self.env.play_type = PlayTypes.human  # We will get human states and observations back
        self.env.render_mode = PlayTypes.machine  # We'll draw these manually
        self.env.max_energy = self.max_energy
        self.env.map_file = self.map_file
        self.env.rand_profile = self.rand_prof
        self.env.num_rows = self.num_rows
        self.env.num_cols = self.num_cols
        self.env.mode = self.mode
        self.env.reset()
        # Report success
        print('Created new environment {0} with GameID: {1}'.format(self.ENV_NAME, self.GAME_ID))

    def done(self):
        #prints end screen with score and escape message
        print("Episode finished after {} turns.".format(self.turn))
        self.game_screen.fill(pg.color.Color(MapColors.game_screen.value))
        game_over = pg.font.Font("Valorant_Font.ttf", 80)
        end_font = pg.font.Font("Valorant_Font.ttf", 60)  # val font
        score_font = pg.font.Font("Valorant_Font.ttf", 40) 
        end_medium_font = pg.font.Font("Valorant_Font.ttf", 30)
        end_small_font = pg.font.Font("Valorant_Font.ttf", 20)
        end1 = game_over.render("GAME OVER", True, pg.color.Color(MapColors.hospital_tile.value))
        self.game_screen.blit(end1, (510, 50))
        end_score = end_font.render("Your Score: " + str(self.info['total_reward']), True, pg.color.Color(MapColors.fire_tile.value))
        self.game_screen.blit(end_score, (530, 180))
        #game stats
        game_stat = score_font.render("Your Stats", True, pg.color.Color(MapColors.fire_tile.value))
        self.game_screen.blit(game_stat, (240, 250))
        performance = score_font.render("Score Performance", True, pg.color.Color(MapColors.fire_tile.value))
        self.game_screen.blit(performance, (950, 250))
        zombie_squished = end_medium_font.render("Zombies Squished: " + str(self.game_score_data['zombies_squished']), True, pg.color.Color(MapColors.text.value))
        pedestrians_squished = end_medium_font.render("Pedestrians Squished: " + str(self.game_score_data['pedestrians_squished']), True, pg.color.Color(MapColors.text.value))
        injured_saved = end_medium_font.render("Injured Saved: " + str(self.game_score_data['injured_saved']), True, pg.color.Color(MapColors.text.value))
        injured_squished = end_medium_font.render("Injured Squished: " + str(self.game_score_data['injured_squished']), True, pg.color.Color(MapColors.text.value))
        end_quit = end_medium_font.render("Quit", True, pg.color.Color(MapColors.text.value))
        self.game_screen.blit(zombie_squished, (200, 350))
        self.game_screen.blit(pedestrians_squished, (200, 450))
        self.game_screen.blit(injured_saved, (200, 550))
        self.game_screen.blit(injured_squished, (200, 650))
        
        #get highscores and all scores for each mode
        if self.mode == 1:
            #get high score
            with open ("m1_high_score.txt", "r+") as m1hs:
                hs = m1hs.read()
                if not hs: #if its empty
                    hs = "0"
                if self.info['total_reward'] > int(hs):
                    new_highscore = end_medium_font.render("High Score: " + str(self.info['total_reward']), True, pg.color.Color(MapColors.text.value))
                    self.game_screen.blit(new_highscore, (640, 240))
                    m1hs.seek(0)
                    m1hs.write(str(self.info['total_reward']))
                    m1hs.truncate()
                else:
                    new_highscore = end_medium_font.render("High Score: " + str(hs), True, pg.color.Color(MapColors.text.value))
                    self.game_screen.blit(new_highscore, (640, 240))
           #get all scores
            with open("m1_scores.txt", "a") as m1as:
                m1as.write(str(self.info['total_reward'])+"\n")
            #get score list
            score_list = []
            with open("m1_scores.txt", "r") as m1as:
                for line in m1as:
                    stripped_line = line.strip()
                    score_list.append(int(stripped_line))
            #performance graph
            plt.style.use("seaborn-dark")
            for param in ['figure.facecolor', 'axes.facecolor', 'savefig.facecolor']:
                plt.rcParams[param] = '#000000'
            for param in ['text.color', 'axes.labelcolor', 'xtick.color', 'ytick.color']:
                plt.rcParams[param] = '#ffffff'
            fig = pylab.figure (figsize = [5, 5], dpi = 90)      
            ax = fig.gca()
            ax.grid(color = '#6665adff')
            ax.plot(score_list, marker = 'o', color = '#ff002b')
            ax.set_xlabel('Game Attempt')
            ax.set_ylabel('Score (Points)')
            x_axis_ticks = len(score_list)
            x_axis_range = range(0, x_axis_ticks)
            plt.xticks(x_axis_range)
            canvas = agg.FigureCanvasAgg(fig)
            canvas.draw()
            renderer = canvas.get_renderer()
            raw_data = renderer.tostring_rgb()
            size = canvas.get_width_height()
            surf = pg.image.fromstring(raw_data, size, "RGB")
            self.game_screen.blit(surf, (940, 300))

        if self.mode == 2:
            #get high score
            with open ("m2_high_score.txt", "r+") as m2hs:
                hs = m2hs.read()
                if not hs: #if its empty
                    hs = "0"
                if self.info['total_reward'] > int(hs):
                    new_highscore = end_medium_font.render("High Score: " + str(self.info['total_reward']), True, pg.color.Color(MapColors.text.value))
                    self.game_screen.blit(new_highscore, (640, 240))
                    m2hs.seek(0)
                    m2hs.write(str(self.info['total_reward']))
                    m2hs.truncate()
                else:
                    new_highscore = end_medium_font.render("High Score: " + str(hs), True, pg.color.Color(MapColors.text.value))
                    self.game_screen.blit(new_highscore, (640, 240))
           #get all scores
            with open("m2_scores.txt", "a") as m2as:
                m2as.write(str(self.info['total_reward'])+"\n")
            #get score list
            score_list = []
            with open("m2_scores.txt", "r") as m2as:
                for line in m2as:
                    stripped_line = line.strip()
                    score_list.append(int(stripped_line))
            #performance graph
            plt.style.use("seaborn-dark")
            for param in ['figure.facecolor', 'axes.facecolor', 'savefig.facecolor']:
                plt.rcParams[param] = '#000000'
            for param in ['text.color', 'axes.labelcolor', 'xtick.color', 'ytick.color']:
                plt.rcParams[param] = '#ffffff'
            fig = pylab.figure (figsize = [5, 5], dpi = 90)      
            ax = fig.gca()
            ax.grid(color = '#6665adff')
            ax.plot(score_list, marker = 'o', color = '#ff002b')
            ax.set_xlabel('Game Attempt')
            ax.set_ylabel('Score (Points)')
            x_axis_ticks = len(score_list)
            x_axis_range = range(0, x_axis_ticks)
            plt.xticks(x_axis_range)
            canvas = agg.FigureCanvasAgg(fig)
            canvas.draw()
            renderer = canvas.get_renderer()
            raw_data = renderer.tostring_rgb()
            size = canvas.get_width_height()
            surf = pg.image.fromstring(raw_data, size, "RGB")
            self.game_screen.blit(surf, (940, 300))
        
        if self.mode == 3: 
            #get high score
            with open ("m3_high_score.txt", "r+") as m3hs:
                hs = m3hs.read()
                if not hs: #if its empty
                    hs = "0"
                if self.info['total_reward'] > int(hs):
                    new_highscore = end_medium_font.render("High Score: " + str(self.info['total_reward']), True, pg.color.Color(MapColors.text.value))
                    self.game_screen.blit(new_highscore, (640, 240))
                    m3hs.seek(0)
                    m3hs.write(str(self.info['total_reward']))
                    m3hs.truncate()
                else:
                    new_highscore = end_medium_font.render("High Score: " + str(hs), True, pg.color.Color(MapColors.text.value))
                    self.game_screen.blit(new_highscore, (640, 240))
           #get all scores
            with open("m3_scores.txt", "a") as m3as:
                m3as.write(str(self.info['total_reward'])+"\n")
            #get score list
            score_list = []
            with open("m3_scores.txt", "r") as m3as:
                for line in m3as:
                    stripped_line = line.strip()
                    score_list.append(int(stripped_line))
            #performance graph
            plt.style.use("seaborn-dark")
            for param in ['figure.facecolor', 'axes.facecolor', 'savefig.facecolor']:
                plt.rcParams[param] = '#000000'
            for param in ['text.color', 'axes.labelcolor', 'xtick.color', 'ytick.color']:
                plt.rcParams[param] = '#ffffff'
            fig = pylab.figure (figsize = [5, 5], dpi = 90)      
            ax = fig.gca()
            ax.grid(color = '#6665adff')
            ax.plot(score_list, marker = 'o', color = '#ff002b')
            ax.set_xlabel('Game Attempt')
            ax.set_ylabel('Score (Points)')
            x_axis_ticks = len(score_list)
            x_axis_range = range(0, x_axis_ticks)
            plt.xticks(x_axis_range)
            canvas = agg.FigureCanvasAgg(fig)
            canvas.draw()
            renderer = canvas.get_renderer()
            raw_data = renderer.tostring_rgb()
            size = canvas.get_width_height()
            surf = pg.image.fromstring(raw_data, size, "RGB")
            self.game_screen.blit(surf, (940, 300))           

        pg.display.update()
        while True:
            mouse = pg.mouse.get_pos()
            quit = False
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key in [pg.K_e]:
                        quit = True
                        break
                if event.type == pg.QUIT:
                    quit = True
                    pg.quit()
                    break
                if event.type == pg.MOUSEBUTTONDOWN:

                    # if the mouse is clicked on the
                    # button the game is terminated
                    if 610 <= mouse[0] <= 910 and 125 <= mouse[1] <= 165:
                        pg.quit()
            if 610 <= mouse[0] <= 910 and 125 <= mouse[1] <= 165:
                pg.draw.rect(self.game_screen, (170,170,170), [610, 125, 300, 40])

            else:
                pg.draw.rect(self.game_screen, (100,100,100), [610, 125, 300, 40])
            self.game_screen.blit(end_quit, (723, 133))
            if quit:
                break
            pg.display.update()
        pg.quit()
        self._cleanup()

    def _cleanup(self):
        self.env.close()

    def _draw_screen(self):
        # Update the screen with the new observation, use the grid object directly
        # Populate each cell
        self.game_screen.fill(pg.color.Color(MapColors.game_screen.value))
        pg.font.init()
        cell_font = pg.font.SysFont(pg.font.get_default_font(), 20)
        player_font = pg.font.SysFont(pg.font.get_default_font(), 25)
        title_font = pg.font.SysFont(pg.font.get_default_font(), 30)
        for r_ in range(self.env.grid.rows):
            for c_ in range(self.env.grid.cols):
                cell = self.env.grid.grid[r_][c_]
                if cell.terrain == Terrains.none:
                    cell_color = pg.color.Color(MapColors.black_tile.value)
                elif cell.terrain == Terrains.out_of_bounds:
                    cell_color = pg.color.Color(MapColors.black_tile.value)
                elif cell.terrain == Terrains.wall:
                    cell_color = pg.color.Color(MapColors.wall_tile.value)
                elif cell.terrain == Terrains.floor:
                    cell_color = pg.color.Color(MapColors.floor_tile.value)
                elif cell.terrain == Terrains.mud:
                    cell_color = pg.color.Color(MapColors.mud_tile.value)
                elif cell.terrain == Terrains.fire:
                    cell_color = pg.color.Color(MapColors.fire_tile.value)
                elif cell.terrain == Terrains.hospital:
                    cell_color = pg.color.Color(MapColors.hospital_tile.value)
                else:
                    raise ValueError('Invalid cell terrain while rendering game image.')

                # Draw the rectangle with the right color for the terrains
                # rect is play area, color, and (left point, top point, width, height)
                pg.draw.rect(self.play_area, cell_color, (c_ * self.cell_size, r_ * self.cell_size,
                                                          self.cell_size, self.cell_size))
                self.game_screen.blit(self.play_area, self.play_area.get_rect())

                # Add in the cell value string
                cell_val = self.env.grid.get_human_cell_value(r_, c_)
                # cell_val = '{},{}'.format(r_, c_)
                #make player symbol color different from other symbols
                if (cell_val == '<') or (cell_val == '>') or (cell_val == 'v') or (cell_val == '^') or (cell_val == '<I') or (cell_val == '>I') or (cell_val == 'vI') or (cell_val == '^I'):
                    text_surf = player_font.render(cell_val, True, pg.color.Color(MapColors.player_color.value))
                else:
                    text_surf = cell_font.render(cell_val, True, pg.color.Color(MapColors.text.value))
                self.play_area.blit(text_surf, ((c_ * self.cell_size) + self.cell_size // 2,
                                                (r_ * self.cell_size) + self.cell_size // 2))
        
        main_font = pg.font.Font("Valorant_Font.ttf", 25)
        text_font = pg.font.SysFont(pg.font.get_default_font(), 22)

        #Title
        title_image = pg.image.load("bwsi_game_title.jpg")
        title_image = pg.transform.smoothscale(title_image, (535,180))
        self.game_screen.blit(title_image, (770, 5))
        
        #General legend
        legend_title = main_font.render("Legend", True, pg.color.Color(MapColors.text.value))
        self.game_screen.blit(legend_title,(775,400))
        general_legend = pg.image.load("state_mark_legend.jpg")
        general_legend = pg.transform.smoothscale(general_legend, (347,316))
        self.game_screen.blit(general_legend, (775, 435))
        #injured fix
        injured_image = pg.image.load("injured.jpg")
        injured_image = pg.transform.smoothscale(injured_image, (75,18))
        
        #mode-specific instructions and legend
        instructions_l1 = text_font.render("A zombie outbreak has occurred in your grid based world. [¬º-°]¬", True, pg.color.Color(MapColors.text.value))
        instructions_l4 = text_font.render("You can only carry 1 injured to a hospital at a time. Others will be squished if ran into.", True, pg.color.Color(MapColors.text.value))
        instructions_l5 = text_font.render("Move using arrow keys (left/right arrow to turn, up arrow to step). Consult legend for more info.", True, pg.color.Color(MapColors.text.value))
        instructions_l6 = text_font.render("Close window to end game. Data will be saved.", True, pg.color.Color(MapColors.text.value))
        if self.mode == 1:
            instructions_title = main_font.render("Instructions - Normal Gamemode", True, pg.color.Color(MapColors.text.value))
            instructions_l2 = text_font.render("As an ambulance, your objective is to save as many injured as you can", True, pg.color.Color(MapColors.text.value))
            instructions_l3 = text_font.render("without running over pedestrians. Running over zombies is an extra bonus.", True, pg.color.Color(MapColors.text.value))
            mode_legend = pg.image.load("m1_legend.jpg")
            mode_legend = pg.transform.smoothscale(mode_legend, (339, 266))
            self.game_screen.blit(mode_legend, (1110, 435))
            self.game_screen.blit(injured_image, (1230, 601))
            self.game_screen.blit(injured_image, (1230, 642))
        if self.mode == 2:
            instructions_title = main_font.render("Instructions - Anarchy Gamemode", True, pg.color.Color(MapColors.text.value))
            instructions_l2 = text_font.render("As an ambulance, you can do whatever you would like -", True, pg.color.Color(MapColors.text.value))
            instructions_l3 = text_font.render("everything results in the same reward. It’s anarchy and chaos in this world. ", True, pg.color.Color(MapColors.text.value))
            mode_legend = pg.image.load("m2_legend.jpg")
            mode_legend = pg.transform.smoothscale(mode_legend, (339, 266))
            self.game_screen.blit(mode_legend, (1110, 435))
            self.game_screen.blit(injured_image, (1230, 600))
            self.game_screen.blit(injured_image, (1230, 641))
        if self.mode == 3:
            instructions_title = main_font.render("Instructions - State of Nature Gamemode", True, pg.color.Color(MapColors.text.value))
            instructions_l2 = text_font.render("As an ambulance, your objective is only self-preservation.", True, pg.color.Color(MapColors.text.value))
            instructions_l3 = text_font.render("This means preserve yourself and kill everyone else.", True, pg.color.Color(MapColors.text.value))
            mode_legend = pg.image.load("m3_legend.jpg")
            mode_legend = pg.transform.smoothscale(mode_legend, (339, 266))
            self.game_screen.blit(mode_legend, (1110, 435))
            self.game_screen.blit(injured_image, (1230, 600))
            self.game_screen.blit(injured_image, (1230, 641))
        
        self.game_screen.blit(instructions_title, (775,180))
        self.game_screen.blit(instructions_l1, (775, 220))
        self.game_screen.blit(instructions_l2, (775, 240))
        self.game_screen.blit(instructions_l3, (775, 260))
        self.game_screen.blit(instructions_l4, (775, 280))
        self.game_screen.blit(instructions_l5, (775, 300))
        self.game_screen.blit(instructions_l6, (775, 320))
        divider = main_font.render("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -", True, pg.color.Color(MapColors.text.value))
        self.game_screen.blit(divider, (775, 335))
        
        #Energy and score
        if self.info:
            energy_remaining = main_font.render("Energy Left: " + str(self.info['total_energy_remaining']), True, pg.color.Color(MapColors.text.value))
            self.game_screen.blit(energy_remaining, (775,360))
            score = main_font.render("Score: " + str(self.info['total_reward']), True, pg.color.Color(MapColors.text.value))
            self.game_screen.blit(score, (1100, 360))  
        else:
            energy_remaining = main_font.render("Energy Left: 50", True, pg.color.Color(MapColors.text.value))
            self.game_screen.blit(energy_remaining, (775,360))
            score = main_font.render("Score: 0", True, pg.color.Color(MapColors.text.value))
            self.game_screen.blit(score, (1100, 360))
             
        pg.display.update()
    def start_screen(self):
        #render start screen text
        self.game_screen.fill(pg.color.Color(MapColors.game_screen.value))
        start_font = pg.font.Font("Valorant_Font.ttf", 30)
        start_font_small = pg.font.Font("Valorant_Font.ttf", 15)
        mode1 = start_font.render("Default Mode",True, pg.color.Color(MapColors.text.value))
        mode1desc1 = start_font_small.render("Default gameplay, save injured,",True, pg.color.Color(MapColors.text.value))
        mode1desc2 = start_font_small.render("avoid pedestrians, run over zombies.",True, pg.color.Color(MapColors.text.value))
        mode2 = start_font.render("Anarchy Mode", True, pg.color.Color(MapColors.text.value))
        mode2desc1 = start_font_small.render("Anarchy gameplay, do whatever", True, pg.color.Color(MapColors.text.value))
        mode2desc2 = start_font_small.render("you want to do. Everything", True, pg.color.Color(MapColors.text.value))
        mode2desc3 = start_font_small.render("is worth the same points.", True, pg.color.Color(MapColors.text.value))
        mode3 = start_font.render("State of Nature", True, pg.color.Color(MapColors.text.value))
        mode3desc1 = start_font_small.render("State of Nature, kill everything", True, pg.color.Color(MapColors.text.value))
        mode3desc2 = start_font_small.render("and preserve yourself. Don't", True, pg.color.Color(MapColors.text.value))
        mode3desc3 = start_font_small.render("save injured people.", True, pg.color.Color(MapColors.text.value))
        select = start_font.render("Select", True, pg.color.Color(MapColors.text.value))
        self.game_screen.blit(mode1, (290, 300))
        self.game_screen.blit(mode2, (630, 300))
        self.game_screen.blit(mode3, (970, 300))
        self.game_screen.blit(mode1desc1, (270, 420))
        self.game_screen.blit(mode1desc2, (250, 440))
        self.game_screen.blit(mode2desc1, (610, 420))
        self.game_screen.blit(mode2desc2, (635, 440))
        self.game_screen.blit(mode2desc3, (643, 460))
        self.game_screen.blit(mode3desc1, (975, 420))
        self.game_screen.blit(mode3desc2, (980, 440))
        self.game_screen.blit(mode3desc3, (1015, 460))
        title_image = pg.image.load("bwsi_game_title.jpg")
        title_image = pg.transform.smoothscale(title_image, (535, 180))
        ambulance = pg.image.load("ambulance.jpg")
        ambulance = pg.transform.smoothscale(ambulance, (200, 200))
        scale = pg.image.load("scale.jpg")
        scale = pg.transform.smoothscale(scale, (200, 200))
        skull = pg.image.load("skull.jpg")
        skull = pg.transform.smoothscale(skull, (200, 200))
        self.game_screen.blit(title_image, (500, 50))
        self.game_screen.blit(ambulance, (310, 500))
        self.game_screen.blit(scale, (655, 500))
        self.game_screen.blit(skull, (1000, 500))
        start_screen = True
        #buttons for start screen(mode specific)
        while start_screen:
            mouse = pg.mouse.get_pos()
            quit = False
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    quit = True
                    start_screen = False
                    pg.quit()
                    break
                if event.type == pg.MOUSEBUTTONDOWN:
                    # if the mouse is clicked on the
                    # button the game is terminated
                    if 260 <= mouse[0] <= 560 and 350 <= mouse[1] <= 390:
                        self.mode = 1
                        start_screen = False
                    elif 610 <= mouse[0] <= 910 and 350 <= mouse[1] <= 390:
                        self.mode = 2
                        start_screen = False
                    elif 960 <= mouse[0] <= 1260 and 350 <= mouse[1] <= 390:
                        self.mode = 3
                        start_screen = False
            if 260 <= mouse[0] <= 560 and 350 <= mouse[1] <= 390:
                pg.draw.rect(self.game_screen, (170,170,170), [260, 350, 300, 40])

            else:
                pg.draw.rect(self.game_screen, (100,100,100), [260, 350, 300, 40])
            if 610 <= mouse[0] <= 910 and 350 <= mouse[1] <= 390:
                pg.draw.rect(self.game_screen, (170, 170, 170), [610, 350, 300, 40])

            else:
                pg.draw.rect(self.game_screen, (100, 100, 100), [610, 350, 300, 40])
            if 960 <= mouse[0] <= 1260 and 350 <= mouse[1] <= 390:
                pg.draw.rect(self.game_screen, (170, 170, 170), [960, 350, 300, 40])
            else:
                pg.draw.rect(self.game_screen, (100, 100, 100), [960, 350, 300, 40])
            if quit:
                pg.quit()
                break
            self.game_screen.blit(select, (355, 358))
            self.game_screen.blit(select, (705, 358))
            self.game_screen.blit(select, (1055, 358))
            pg.display.update()
    def run(self):
        pg.init()
        self.game_screen = pg.display.set_mode((1470, 800))
        print('Starting new game with human play!')
        # Set up pygame loop for game, capture actions, and redraw the screen on action
        self.env.reset()
        self.env.render_mode = PlayTypes.machine  # We'll draw the screen manually and not render each turn
        pg.display.set_caption('SGW Human Play')
        self.play_area = pg.Surface((self.env.grid.rows * self.cell_size, self.env.grid.cols * self.cell_size))
        self.play_area.fill(pg.color.Color(MapColors.play_area.value))
        self.game_screen.fill(pg.color.Color(MapColors.game_screen.value))
        self._draw_screen()

        # Main game loop, capture window events, actions, and redraw the screen with updates until game over
        game_exit = False
        while not game_exit:
            for event in pg.event.get():

                # Exit game upon window close
                if event.type == pg.QUIT:
                    game_exit = True
                    self.done()

                if self.turn < self.max_turn and not self.is_game_over:

                    # Execute main turn logic
                    # Start by getting the action, only process a turn if there is an actual action
                    # Catch the player inputs, capture key stroke
                    action = None
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_ESCAPE:
                            game_exit = True
                            pg.quit()
                            self.done()
                        if event.key in [pg.K_w, pg.K_SPACE, pg.K_UP, pg.K_3]:
                            action = Actions.step_forward
                        if event.key in [pg.K_a, pg.K_LEFT, pg.K_1]:
                            action = Actions.turn_left
                        if event.key in [pg.K_d, pg.K_RIGHT, pg.K_2]:
                            action = Actions.turn_right
                        if event.key in [pg.K_s, pg.K_DOWN, pg.K_0]:
                            action = Actions.none

                    if action is not None:
                        if action in [Actions.step_forward, Actions.turn_right, Actions.turn_left, Actions.none]:
                            # We have a valid action, so let's process it and update the screen
                            encoded_action = self.env.encode_raw_action(action)  # Ensures clean action
                            action_decoded = self.env.decode_raw_action(encoded_action)

                            # Take a step, print the status, render the new state
                            observation, reward, done, info, game_score_data = self.env.step(encoded_action)
                            self.info = info
                            self.env.pp_info()
                            self.is_game_over = done
                            self.game_score_data = game_score_data


                            # Write action and stuff out to disk.
                            data_to_log = {
                                'game_id': str(self.GAME_ID),
                                'turn': self.turn,
                                "squish/save data": self.game_score_data
                            }
                            with open(self.DATA_LOG_FILE_NAME, 'a') as f_:
                                f_.write(json.dumps(data_to_log) + '\n')
                                f_.close()
                            size = os.path.getsize('m_data_log.json')
                            if size == 4000000:
                                with open(sys.argv[1], "r+", encoding="utf-8") as file:

                                    # Move the pointer (similar to a cursor in a text editor) to the end of the file
                                    file.seek(0, os.SEEK_END)

                                    # This code means the following code skips the very last character in the file -
                                    # i.e. in the case the last line is null we delete the last line
                                    # and the penultimate one
                                    pos = file.tell() - 1

                                    # Read each character in the file one at a time from the penultimate
                                    # character going backwards, searching for a newline character
                                    # If we find a new line, exit the search
                                    while pos > 0 and file.read(1) != "\n":
                                        pos -= 1
                                        file.seek(pos, os.SEEK_SET)

                                    # So long as we're not at the start of the file, delete all the characters ahead
                                    # of this position
                                    if pos > 0:
                                        file.seek(pos, os.SEEK_SET)
                                        file.truncate()

                            # Tick up turn
                            self.turn += 1
                            if self.is_game_over:
                                game_exit = True
                                self.done()

                            # Draw the screen
                            if not self.is_game_over:
                                self._draw_screen()

                else:
                    # Else end the game
                    game_exit = True
                    self.done()
        pg.quit()
