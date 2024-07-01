from os import environ, popen

from tss import tss_gen_private_key, tss_get_public_key

SEED_PREFIX = '1234567890_1234567890_1234567890_'

log_level = environ['DDS_LOG_LEVEL']
network = environ['DDS_NETWORK']
port = int(environ['DDS_PORT'])
num_hosts = int(environ['DDS_NUM_CORRECT']) + int(environ['DDS_NUM_BYZ'])
is_byzantine = environ['DDS_IS_BYZANTINE'] == 'true'

net_prefix = '.'.join(network.split('.')[:-1])
processes = set([
	f'{net_prefix}.{num}'
	for num in range(2, num_hosts + 2)
])

cur_process = popen('/bin/hostname -i').read().strip()

keys = {}

for process in processes:
	keys[process] = [ None, None ]

	seed = (SEED_PREFIX + process).encode('ascii')
	private_key = tss_gen_private_key(seed)

	if process == cur_process:
		keys[process][0] = private_key

	keys[process][1] = tss_get_public_key(private_key)
