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

Setup

### Technologies

Prova

### Implementation

Prova

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
