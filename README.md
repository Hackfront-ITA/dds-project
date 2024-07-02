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

Prova

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

Also, since difference components use the same BeB component, to differentiate between its users, a "class id" is added as an header in the packet.

There is an issue: packet size, so its payload, is limited by the MTU of the network interface, which typically is 1500. Since we use a virtual interface, we can increase a bit the MTU and don't care about this limitation for our experiments.

#### Threshold signature scheme

TSS using BLS

### Experiments

Prova

### Dependability evaluation

#### Performance

Message delay related to our implementation

##### Best case

No conflicting light certificates, exactly t0 failures -> 2 * (n - t0) messages
Submit round + light certificate round, sent by n - t0 processes

##### Worst case

Conflicting light certificates, no crash failures but byzantine behavior -> 3 * n messages -> 3 * n * n packets

#### Availability

t0 <= ceil(n/3) - 1 (tre gruppi A, B, C a pagina 8 destra in fondo)

99.99 % globale -> formula in parallelo inversa -> availability del singolo processo
0.9999 = 1 - (1 - An)^n -> 1 - pow(0.0001, 1/n) -> 60% con 10 processi
