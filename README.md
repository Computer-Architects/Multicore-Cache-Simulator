<!-- Header -->
# Multicore Cache Simulator

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#adding-a-new-algorithm">Adding a new protocol</a></li>
    <li><a href="#adding-a-new-testcase">Adding a new testcase</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

Implemented a multicore cache simulator to simulate and compare various cache coherence protocols.

### Protocols
The protocols implemented are:
* MSI
* MOSI
* MESI
* MOESI

### Built With

Code is in python.

<!-- GETTING STARTED -->
## Getting Started

### Installation

1. Clone the repo
   
   ```sh
   $ git clone https://github.com/Computer-Architects/Multicore-Cache-Simulator.git
   ```

<!-- USAGE EXAMPLES -->
## Usage

```sh
$ python run.py --help
usage: run.py [-h] [--protocol PROTOCOL] [--cacheSz CACHESZ]
              [--blockSz BLOCKSZ] [--a A] [--testcase TESTCASE]

optional arguments:
  -h, --help           show this help message and exit
  --protocol PROTOCOL # default protocol is MSI
  --cacheSz CACHESZ
  --blockSz BLOCKSZ
  --a A  # associativity of the cache
  --testcase TESTCASE # testcase id
```
A general way to use the simulator
```sh
$ python run.py --protocol PROTOCOL --cacheSz CACHESZ --blockSz BLOCKSZ --a A --testcase TESTCASE
```
Here is an example
```sh
$ python run.py --testcase 1
```

<!-- Adding a new protocol -->
## Adding a new protocol
1. Create a cache implementing the protocol similar to [msi_cache.py](msi_cache.py)

2. Add your protocol to [cache_sim.py](cache_sim.py)
    * Import your protocol 
    ```python
    from mesi_cache import MESI_Cache, Processor, Bus
    from msi_cache import MSI_Cache
    from mosi_cache import MOSI_Cache
    from moesi_cache import MOESI_Cache
    ```
    * Add the protocol to [Computer](https://github.com/Computer-Architects/Multicore-Cache-Simulator/blob/afc7f8123abd1c13f759090e71b449f4fc7dcf66/cache_sim.py#L13)
    ```python
    if protocol == 'MSI':
        self.caches = [MSI_Cache(i, cacheSz, blockSz, a, self.bus, self.processors[i]) for i in range(n)]
    elif protocol == 'MESI':
        self.caches = [MESI_Cache(i, cacheSz, blockSz, a, self.bus, self.processors[i]) for i in range(n)]
    elif protocol == 'MOSI':
        self.caches = [MOSI_Cache(i, cacheSz, blockSz, a, self.bus, self.processors[i]) for i in range(n)]
    elif protocol == 'MOESI':
        self.caches = [MOESI_Cache(i, cacheSz, blockSz, a, self.bus, self.processors[i]) for i in range(n)]
    else:
        raise Exception('No such protocol !!!')
    ```

<!-- Adding a new testcase -->
## Adding a new testcase
Format of a testcase:
* Each testcase is a directory with the name *testcase<test_id>*
* The directory contains a config file which stores the number of cores(processors) in the testcase
* In addition, it contains files with the names *p<processor_id>.trace*. Each file corresponds to processor *<processor_id>*. The file stores the read / write requests made to the processor.

Take a look at this [example](https://github.com/Computer-Architects/Multicore-Cache-Simulator/tree/main/testcases/testcase1).

To add a new testcase create a testcase in a similar manner and add it to the directory [testcases/](https://github.com/Computer-Architects/Multicore-Cache-Simulator/tree/main/testcases)

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. There are many exciting protocols which can be implemented and added to this simulator. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.



<!-- CONTACT -->
## Team

Rishi Agarwal <br>
Samad Koita <br>
Sumanyu Ghoshal <br>
Parth Sangani <br>


Project Link: [https://github.com/Computer-Architects/Multicore-Cache-Simulator.git](https://github.com/Computer-Architects/Multicore-Cache-Simulator.git)



<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

[Cache Coherence Protocols: Evaluation Using a Multiprocessor Simulation Model](https://people.eecs.berkeley.edu/~kubitron/courses/cs252-S12/handouts/papers/p273-archibald.pdf)

