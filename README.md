# Accountable Byzantine Consensus
Project for Dependable Distributed Systems course

[Repository](https://github.com/Hackfront-ITA/dds-project)

### Project description
The goal of the project is to implement an accountable consensus primitive based on this [paper](https://doi.org/10.1016/j.jpdc.2023.104743) ([archived](./docs/paper.pdf)).
There are no constraints on the programming language or libraries to be used, nor on the environment (local machine, docker, cloud free tiers, simulator).
Part of the project is to perform a dependability evaluation (both from a functionality and performance point of view).
Crash failures must be considered, whereas some Byzantine misbehaviours could be
considered in the evaluation.

[Full details](./docs/request.pdf)

### People
- Alessandro Cecchetto -- 1941039
- Emanuele Roccia -- 1967318

## Contents
- [Setup](#setup)
- [Technologies](#technologies)
- [Implementation](#implementation)
- [Experiments](#experiments)
- [Dependability evaluation](#dependability-evaluation)

### Setup

Customize [.env](./.env) file according to your preferences:

```shell
DDS_LOG_LEVEL="INFO"  ## Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

DDS_NETWORK="172.21.0.0/16"   ## Subnet used by virtual network
DDS_PORT="4678"       ## Port used by broadcast module

DDS_NUM_CORRECT="5"   ## Number of correct processes
DDS_NUM_BYZ="3"       ## Number of byzantine processes
DDS_T0_AC="3"         ## Max number of failures in confirmer according to paper
```

To bring up the whole infrastructure a single command is necessary:

```shell
cd dds-project
docker compose up
```

### Technologies

This project uses Docker to create a virtual environment, with correct processes and byzantine processes, that communicate together via a virtual network.

Everything is described in [docker-compose.yml](./docker-compose.yml) file.

For the code part, we used Python as it is a powerful language.

- Docker (with compose)
- Python
- TSS using blspy (binding for blst in C)

### Implementation

A (correct) node process is composed of four components, that communicate together via an event-based interface.

- Confirmer
- Consensus
- Failure detector
- Best effort broadcast

#### Event-based interface

Every component is a derived class from an [ObjectWithEvents](https://stackoverflow.com/a/6158658) class, from which it inherits the `on()` and `trigger()` methods.
The purpose is to make the code as similar as possible to the pseudo-code provided by the study material and the ABC paper.

An example of the API provided by the ObjectWithEvents class:
```python
def on_decision(_, decision):
	logger.info(f'Consensus decided {decision}')

consensus.on('decide', on_decision)

consensus.trigger('propose', value)
```

#### Best effort broadcast

Virtually every component that we use needs an underlying best effort broadcast primitive.
We implemented BeB on top of UDP. Simply when it receives a `send` event it broadcast an UDP packet to the broadcast address of the subnet, so it reaches every host in it.
Every node listens to the broadcast address and a fixed port defined in [.env](./.env) file. When a packet arrives, a `receive` event is triggered, to signal all the listening components.

Events coming from and to the BeB component carry also some parameters, which are serialized/de-serialized using JSON to build the packet payload.

Also, since different components use the same BeB component, to differentiate between its users, a "class id" is added to the packet as an header.

There is an issue: packet size, so its payload, is limited by the MTU of the network interface, which typically is 1500 bytes. Since we use a virtual interface, we can increase a bit the MTU and don't care about this limitation for our experiments.

#### Key exchange

The TSS scheme that we use requires that every process has its own private key (to sign messages) and the public key of every other process (to verify signatures).

To quickly allow all the processes to have this information, not taking into account privacy issues, each process in [config.py](./src/config.py):

- Generates the list of running processes, identified by their IPv4 address
- Uses them as a seed to generate every process private key
- For each of them derives the public key and stores them in an dictionary indexed by process address

For all processes, except the current process, the private key is discarded. In this way every process has the same set of public key, but the corresponding private key for only itself.

#### Light certificate message
One difference between the paper and our implementation is the content of the light certificate message.

While in the paper the light certificate consists only of the combined signature, in the TSS scheme that we use this is not enough for validation.

In addition, an ordered list of public keys of the participating processes is required. To address this, we included the instance *from* array within the light certificate message, that contain the process list in the necessary order.

The process then builds the PK array by mapping every process with their public key.

#### Certificate conflict checking
To check conflicts between light certificates, a dictionary is used to store for each process the set of values that it has confirmed.

As a new light certificate arrives, the validity of certificate is checked, otherwise discarded.
Then, for each process contained in it, we add to its set in the dictionary the value associated to the certificate.
If there is a set in the dictionary that has more than one value, it is for sure a byzantine process, so the the full certificate is sent and the confirmer algorithm continues.

We removed the array of obtained light certificates that was included in the paper because it was no longer useful.

An analogous technique is used for the full certificates, but instead of using sets of values we use sets of messages, but the check is basically the same.

### Experiments

Confirmer test with
- 2 different values and 3 byzantines
- Some hosts not available (crashed or different values proposed)


### Dependability evaluation

#### Performance

Message delay related to our implementation

##### Best case

No conflicting light certificates, exactly t0 failures -> 2 * (n - t0) messages
Submit round + light certificate round, sent by n - t0 processes

##### Worst case

Conflicting light certificates, no crash failures but byzantine behavior -> 3 * n messages -> 3 * n * n packets

#### Availability

With respect to the availability evaluation, we consider the set of processes in the system in the following arrangement:

![Availability diagram](./res/availability.png "Availability diagram")

The whole system is available only if the number of faulty processes does not exceed $t_0$.
This is justified by the fact that the confirmer triggers the confirmation when it receives $n - t_0$ submissions related the local value, so it needs at least that number of process. The flooding consensus that we used does not have a requirement on minimum number of processes.

We can imagine the system with a *core* of $n - t_0$ processes that are in series, and other $t_0$ processes in parallel to the core that *support* it.
As the faults occur, the *support* processes go down. If the number of faults exceed $t_0$, the processes in the *core* go down, so the entire series.

This is only a virtual arrangement: processes do not strictly belong to a set or the other.

We define $A_t$ as the availability of the entire system, while $A = A_c = A_s$ as the availability of a single process.

Availability of nodes in parallel: $A_{parallel} = 1 - [ \prod{(1 - A_i)} ]$

Availability of nodes in series: $A_{series} = \prod{A_i}$

Availability of the system:
$$ A_t = 1 - [ \prod_{s \in support}{(1 - A_s)} ] \cdot [ 1 - \prod_{c \in core}{A_c} ] $$

$$ A_t = 1 - [ {(1 - A)}^{t_0} ] \cdot [ 1 - {A}^{n - t_0} ] $$


t0 <= ceil(n/3) - 1 (tre gruppi A, B, C a pagina 8 destra in fondo)
