import os
import argparse
from SGWMachinePlay import SGW
from gym_sgw.envs.enums.Enums import MapProfiles

parser = argparse.ArgumentParser(description='CLI Argument Parser for Human Play.')
parser.add_argument('--agentfile', help='Agent file path and file name.', default='sgw_dqn_rl-agent-test_weights.h5f')
parser.add_argument('--outfile', help='Data logging file name.', default='m_data_log.json')
parser.add_argument('--creation', help='Allow creation of output file.', default=True, action='store_true')
parser.add_argument('--mode', help='Train the machine on a mode.', type=int, default=1)


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
    agent_file = args.agentfile
    data_log_file = args.outfile
    map_file = None  # 'gym_sgw/envs/maps/_SampleMap.xls'  # None will generate a random map, map files have top priority
    max_energy = 50
    rand_prof = MapProfiles.custom_made
    num_rows = 25
    num_cols = 25
    mode = args.mode

    # Create and run game with those params
    sgw_env = SGW(
        agent_file=agent_file,
        data_log_file=data_log_file,
        map_file=map_file,
        max_energy=max_energy,
        rand_prof=rand_prof,
        num_rows=num_rows,
        num_cols=num_cols,
        mode=mode
    )
    sgw_env.run()
