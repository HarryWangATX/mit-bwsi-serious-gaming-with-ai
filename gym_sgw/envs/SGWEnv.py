from typing import Union
import gym
from gym import spaces
from gym_sgw.envs.enums.Enums import Actions, PlayTypes, MapProfiles, Terrains, MapObjects, Normal, Anarchy, StateOfNature
from gym_sgw.envs.model.Grid import Grid
from gym_sgw.envs.Print_Colors.PColor import PBack


class SGW(gym.Env):

    def __init__(self):
        # Tunable parameters
        self.play_type = PlayTypes.machine
        self.render_mode = PlayTypes.machine
        self.max_energy = 50
        self.map_file = None
        self.rand_profile = MapProfiles.custom_made
        self.mode = 1
        self.game_score_data = {
            'zombies_squished': 0,
            'pedestrians_squished': 0,
            'injured_saved': 0,
            'injured_squished': 0
        }
        # Grid set up
        self.num_rows = 20
        self.num_cols = 20
        self.grid = Grid(map_file=self.map_file, cols=self.num_cols, rows=self.num_rows,
                         random_profile=self.rand_profile, mode=self.mode)
        # Main parameters
        self.total_score = 0
        self.energy_used = 0
        self.is_game_over = False
        self.latest_action = self.decode_raw_action(Actions.none)
        self.turns_executed = 0
        # Defining spaces
        self._num_actions = len(Actions)
        self.action_space = None  # Build on reset, which is called after the init, don't build the grid twice
        self.observation_space = None  # Build on reset, which is called after the init, don't build the grid twice
        self.reset()

    def reset(self):
        self.grid = Grid(map_file=self.map_file, cols=self.num_cols, rows=self.num_rows,
                         random_profile=self.rand_profile, mode=self.mode)
        self.total_score = 0
        self.energy_used = 0
        self.max_energy = self.grid.map_max_energy if self.grid.map_max_energy is not None else self.max_energy
        self.is_game_over = False
        self.latest_action = self.decode_raw_action(Actions.none)
        self.turns_executed = 0
        self._num_actions = len(Actions)
        self.action_space = spaces.Discrete(self._num_actions)
        self.observation_space = spaces.Box(low=0, high=70, shape=(self.num_rows + 1, self.num_cols), dtype='uint8')
        obs = self.get_obs()
        return obs

    def step(self, raw_action: Actions):
        # Ensure that our type assertion holds
        action = self.encode_raw_action(raw_action)

        # Adjudicate turn
        turn_score, turn_energy, is_done = self._do_turn(action=action)
        self.latest_action = self.decode_raw_action(action)
        self.turns_executed += 1

        # Update score and turn counters
        self.total_score += turn_score
        self.energy_used += turn_energy
        # Check if done
        if is_done or (-1 * self.energy_used >= self.max_energy):
            self.is_game_over = True

            #testing data collection results -> print these once the game ends

        # Report out basic information for step
        self.game_score_data = {
            'mode': self.mode,
            'total_reward': self.total_score,
            'zombies_squished': self.grid.zombies_squished,
            'pedestrians_squished': self.grid.pedestrians_squished,
            'injured_saved': self.grid.injured_saved,
            'injured_squished': self.grid.injured_squished
        }
        obs = self.get_obs()
        info = {'turn_reward': turn_score, 'total_reward': self.total_score,
                'turn_energy_used': turn_energy, 'total_energy_used': self.energy_used,
                'total_energy_remaining': self.max_energy + self.energy_used}

        return obs, self.total_score, self.is_game_over, info, self.game_score_data

    def _do_turn(self, action):
        score, energy, done = self.grid.do_turn(action=action)
        return score, energy, done

    def get_obs(self):
        if self.play_type == PlayTypes.human:
            return self.grid.human_encode(turns_executed=self.turns_executed,
                                          action_taken=self.latest_action,
                                          energy_remaining=(self.max_energy + self.energy_used),
                                          game_score=self.total_score)
        elif self.play_type == PlayTypes.machine:
            return self.grid.machine_encode(turns_executed=self.turns_executed,
                                            action_taken=self.latest_action,
                                            energy_remaining=(self.max_energy + self.energy_used),
                                            game_score=self.total_score)
        else:
            raise ValueError('Failed to find acceptable play type.')

    def render(self, mode: PlayTypes = PlayTypes.human):
        if self.render_mode == PlayTypes.human or mode == PlayTypes.human:
            return self.grid.human_render(turns_executed=self.turns_executed,
                                          action_taken=self.latest_action,
                                          energy_remaining=(self.max_energy + self.energy_used),
                                          game_score=self.total_score, cell_size=30)
        elif self.render_mode == PlayTypes.machine or mode == PlayTypes.machine:
            return self.grid.machine_render(turns_executed=self.turns_executed,
                                            action_taken=self.latest_action,
                                            energy_remaining=(self.max_energy + self.energy_used),
                                            game_score=self.total_score)
        else:
            raise ValueError('Failed to find acceptable play type.')

    def pp_info(self):
        self.grid.pp_info(turns_executed=self.turns_executed,
                          action_taken=self.latest_action,
                          energy_remaining=(self.max_energy + self.energy_used),
                          game_score=self.total_score)

    @staticmethod
    def encode_raw_action(input_str: Union[str, Actions]) -> Actions:
        # Takes in some input string and tries to parse it to a valid action, encoding it in our enum
        # Use this if you want to go from a string or key press to an Actions Enum!
        if input_str in ['none', '', 'r_key', 0, '0', Actions.none]:
            return Actions.none
        if input_str in ['turn_left', 'left', 'left_arrow_key', 'a_key', 1, '1', Actions.turn_left]:
            return Actions.turn_left
        if input_str in ['turn_right', 'right', 'right_arrow_key', 'd_key', 2, '2', Actions.turn_right]:
            return Actions.turn_right
        if input_str in ['step_forward', 'forward', 'step', 'move', 'space_key', 3, '3', Actions.step_forward]:
            return Actions.step_forward
        print('WARNING: no valid action found while encoding action: {}'.format(input_str))
        return Actions.none

    @staticmethod
    def decode_raw_action(action: Actions) -> (str, int):
        # Reverse process of the encoding, takes in an enum action and spits out an unboxable decoding of the action
        # Use this to make the Actions Enum more readable, returns the label and int value for the enum.
        # Use if you want to go from Enum to something more understandable.
        return action.name, action.value

    @staticmethod
    def print_player_action_selections():

        # Build up console output
        buffer = '*' * 35
        player_action_string = PBack.blue + buffer + PBack.reset + '\n'

        player_action_string += PBack.blue + '**||' + PBack.reset + \
                                PBack.purple + ' Action ID'.center(10) + PBack.reset + \
                                PBack.blue + '||' + PBack.reset + \
                                PBack.purple + ' Action'.center(15) + PBack.reset + \
                                PBack.blue + '||**' + PBack.reset + '\n'

        for i in range(len(Actions)):
            act_val = str(Actions(i).value)
            act_name = Actions(i).name
            player_action_string += PBack.blue + '**||' + PBack.reset + \
                                    act_val.center(10) + \
                                    PBack.blue + '||' + PBack.reset + \
                                    act_name.center(15) + \
                                    PBack.blue + '||**' + PBack.reset + '\n'

        player_action_string += PBack.blue + buffer + PBack.reset

        print(player_action_string)
        return player_action_string

    # @staticmethod
    def print_state_key(self):

        # Build up console output
        buffer = '*' * 35
        state_key_string = PBack.blue + buffer + PBack.reset + '\n'

        state_key_string += PBack.blue + '**||' + PBack.reset + \
                            PBack.purple + 'State Mark'.center(10) + PBack.reset + \
                            PBack.blue + '||' + PBack.reset + \
                            PBack.purple + 'Meaning'.center(15) + PBack.reset + \
                            PBack.blue + '||**' + PBack.reset + '\n'

        for terrain_index in range(len(Terrains)):
            # Get the right color from the map
            if Terrains(terrain_index) == Terrains.none:
                cell_color = PBack.black
            elif Terrains(terrain_index) == Terrains.out_of_bounds:
                cell_color = PBack.black
            elif Terrains(terrain_index) == Terrains.wall:
                cell_color = PBack.darkgrey
            elif Terrains(terrain_index) == Terrains.floor:
                cell_color = PBack.lightgrey
            elif Terrains(terrain_index) == Terrains.mud:
                cell_color = PBack.brown
            elif Terrains(terrain_index) == Terrains.fire:
                cell_color = PBack.tangerine
            elif Terrains(terrain_index) == Terrains.hospital:
                cell_color = PBack.neonred
            else:
                raise ValueError('Invalid cell terrain while printing state key.')
            name = Terrains(terrain_index).name
            state_key_string += PBack.blue + '**||' + PBack.reset + \
                                cell_color + ''.center(10) + \
                                PBack.blue + '||' + PBack.reset + \
                                name.center(15) + \
                                PBack.blue + '||**' + PBack.reset + '\n'

        for mapobject_index in range(len(MapObjects)):
            if MapObjects(mapobject_index) == MapObjects.none:
                cell_val = '?'
            elif MapObjects(mapobject_index) == MapObjects.player:
                cell_val = '<,>,^,v'
            elif MapObjects(mapobject_index) == MapObjects.battery:
                cell_val = 'B'
            elif MapObjects(mapobject_index) == MapObjects.injured:
                cell_val = 'I'
            elif MapObjects(mapobject_index) == MapObjects.pedestrian:
                cell_val = 'P'
            elif MapObjects(mapobject_index) == MapObjects.zombie:
                cell_val = 'Z'
            else:
                raise ValueError('Invalid cell MapObject while printing state key.')
            name = MapObjects(mapobject_index).name
            state_key_string += PBack.blue + '**||' + PBack.reset + \
                                cell_val.center(10) + \
                                PBack.blue + '||' + PBack.reset + \
                                name.center(15) + \
                                PBack.blue + '||**' + PBack.reset + '\n'

        state_key_string += PBack.blue + buffer + PBack.reset
        state_key_string += "\n" + PBack.blue + "**||" + PBack.reset + \
                            PBack.purple + 'Action/Item'.center(18) + PBack.reset + \
                            PBack.blue + '||' + PBack.reset + \
                            PBack.purple + 'Energy'.center(7) + PBack.reset + \
                            PBack.blue + '||**' + PBack.reset + '\n'

        state_key_string += PBack.blue + "**||" + PBack.reset + "Take Step".center(18) + \
                            PBack.blue + "||" + PBack.reset + "-1".center(7) + \
                            PBack.blue + "||**" + PBack.reset + "\n"

        state_key_string += PBack.blue + "**||" + PBack.reset + "Battery".center(18) + \
                            PBack.blue + "||" + PBack.reset + "20".center(7) + \
                            PBack.blue + "||**" + PBack.reset + "\n"

        state_key_string += PBack.blue + "**||" + PBack.reset + "Mud".center(18) + \
                            PBack.blue + "||" + PBack.reset + "-2".center(7) + \
                            PBack.blue + "||**" + PBack.reset + "\n"

        state_key_string += PBack.blue + "**||" + PBack.reset + "Fire".center(18) + \
                            PBack.blue + "||" + PBack.reset + "-5".center(7) + \
                            PBack.blue + "||**" + PBack.reset + "\n"

        state_key_string += PBack.blue + buffer + PBack.reset

        state_key_string += "\n" + PBack.blue + "**||" + PBack.reset + \
                            PBack.purple + 'Action'.center(18) + PBack.reset + \
                            PBack.blue + '||' + PBack.reset + \
                            PBack.purple + 'Points'.center(7) + PBack.reset + \
                            PBack.blue + '||**' + PBack.reset + '\n'

        if self.mode == 1:
            # Normal mode points
            for reward in Normal:
                state_key_string += PBack.blue + "**||" + PBack.reset

                if reward.name == "RESCUE_REWARD":
                    action_name="Rescue Injured"
                elif reward.name == "PED_PENALTY":
                    action_name="Squish Pedestrian"
                elif reward.name == "VIC_PENALTY":
                    action_name="Squish Injured"
                elif reward.name == "ZOMBIE_REWARD":
                    action_name="Squish Zombie"
                else:
                    action_name=reward.name

                state_key_string += action_name.center(18) + \
                                    PBack.blue + "||" + PBack.reset + str(reward.value).center(7) + \
                                    PBack.blue + "||**" + PBack.reset + "\n"

        elif self.mode == 2:
            # Anarchy mode points
            for reward_name, reward_value in Anarchy.__members__.items():
                #creates ordered dict from enums bc there are duplicate values
                # (would otherwise be skipped when iterating over)
                state_key_string += PBack.blue + "**||" + PBack.reset

                if reward_name == "RESCUE_REWARD":
                    action_name = "Rescue Injured"
                elif reward_name == "PED_PENALTY":
                    action_name = "Squish Pedestrian"
                elif reward_name == "VIC_PENALTY":
                    action_name = "Squish Injured"
                elif reward_name == "FIRE_PENALTY":
                    action_name = "Fire"
                elif reward_name == "ZOMBIE_REWARD":
                    action_name = "Squish Zombie"
                else:
                    action_name = reward_name

                state_key_string += action_name.center(18) + \
                                    PBack.blue + "||" + PBack.reset + str(reward_value.value).center(7) + \
                                    PBack.blue + "||**" + PBack.reset + "\n"

        elif self.mode == 3:
            # State of nature mode points
            for reward_name, reward_value in StateOfNature.__members__.items():
                state_key_string += PBack.blue + "**||" + PBack.reset

                if reward_name == "RESCUE_REWARD":
                    action_name = "Rescue Injured"
                elif reward_name == "PED_PENALTY":
                    action_name = "Squish Pedestrian"
                elif reward_name == "VIC_PENALTY":
                    action_name = "Squish Injured"
                elif reward_name == "FIRE_PENALTY":
                    action_name = "Fire"
                elif reward_name == "ZOMBIE_REWARD":
                    action_name = "Squish Zombie"
                else:
                    action_name = reward_name

                state_key_string += action_name.center(18) + \
                                    PBack.blue + "||" + PBack.reset + str(reward_value.value).center(7) + \
                                    PBack.blue + "||**" + PBack.reset + "\n"

        state_key_string += PBack.blue + buffer + PBack.reset

        print(state_key_string)
        return state_key_string


if __name__ == '__main__':
    # Quick Demo of class
    my_sgw = SGW()  # Set up
    my_sgw.play_type = PlayTypes.machine
    my_sgw.render_mode = PlayTypes.machine
    my_sgw.max_energy = 50
    my_sgw.map_file = None
    my_sgw.rand_profile = MapProfiles.custom_made
    my_sgw.num_rows = 20
    my_sgw.num_cols = 20
    my_sgw.mode = 1

    # Select an action (human or from agent)
    my_sgw.print_player_action_selections()
    action_selection = Actions.step_forward

    # Execute and advance the game
    new_obs, new_score, game_over, turn_info = my_sgw.step(raw_action=action_selection)

    # Render for a human
    my_sgw.print_state_key()
    my_sgw.render(mode=PlayTypes.human)
