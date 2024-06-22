from os import environ

log_level = environ['DDS_LOG_LEVEL']
network = environ['DDS_NETWORK']
port = int(environ['DDS_PORT'])
num_hosts = int(environ['DDS_NUM_HOSTS'])

net_prefix = '.'.join(network.split('.')[:-1])
processes = set([ f'{net_prefix}.{num}' for num in range(2, num_hosts + 2) ])
