import os
import argparse
from SGWHumanPlay import SGW_human
from gym_sgw.envs.enums.Enums import MapProfiles
from gym_sgw.envs.SGWEnv import SGW

parser = argparse.ArgumentParser(description='CLI Argument Parser for Human Play.')
parser.add_argument('--outfile', help='Data logging file name.', default='data_log.json')
parser.add_argument('--creation', help='Allow creation of output file.', default=True, action='store_true')
parser.add_argument('--mode', help='Chooses different modes, 1=Normal, 2=Anarchy, 3=State Of Nature', type=int, default=1)



def validate_data(out_file, allow_creation=False):
    if allow_creation and not os.path.exists(out_file):
        f = open(out_file, 'w+')
        f.close()
    if not os.path.isfile(out_file):
        raise EnvironmentError('Bad filename provided in CLI arguments.')


if __name__ == '__main__':
    # Parse CLI Args
    args = parser.parse_args()
    os.system('mode con: cols=125 lines=62')
    validate_data(args.outfile, allow_creation=args.creation)

    # Set runtime args
    data_log_file = args.outfile
    map_file = None # gym_sgw/envs/maps/classic_trolley-ambiguous.xls'  # None -> random map, map files have top priority
    max_energy = 50
    rand_prof = MapProfiles.custom_made
    num_rows = 25
    num_cols = 25
    mode = args.mode

    #legend = SGW()
    #legend.mode = mode #works if I manually set it to 1/2/3 then run this file w/ play button, not if I run from command line
    #print(legend.mode)
    #legend.print_state_key()

    # Create and run game with those params
    sgw_env = SGW_human(
        data_log_file=data_log_file,
        map_file=map_file,
        max_energy=max_energy,
        rand_prof=rand_prof,
        num_rows=num_rows,
        num_cols=num_cols,
        mode=mode
    )
    sgw_env.run()
