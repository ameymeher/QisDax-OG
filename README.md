# Qisdax, qiskit to DAX Compiler
This document describes the project qisdax, whose goal is to compile quantum circuit code written in the high-level language qiskit into the lower level descriptive language DAX.

# Installation Instructions

1. Install [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)/[Anaconda](https://www.anaconda.com/products/distribution)
2. In the root of the repository, run
```
conda env create -f environment.yml
conda activate qisdax
pip install -e .
```
3. Usage examples can be found in the `tests/` directory. Create a `.dax` file as specified [here](https://gitlab.com/duke-artiq/dax-program-sim#usage), then run:
`python [filename]`

### DAX-Example installation
* The dax-example project is how simulation will be brought into this qisdax compiler
* to install the dax-example project follow the instructions on their repository [here](https://gitlab.com/duke-artiq/dax-example)

# Development Information
## File Descriptions

### qiskit/providers/dax/dax_provider.py
* The provider object holds information inside it about what backends it has available to it.
* Currently our provider only points towards the DAXGenerator, but if we wanted to add in simulation abilities, linking in a new backend here is where you would probably do that.

### qiskit/providers/dax/dax_backend.py
* The backend object is where a few different things are dispatched
* The load_config() method is how we describe the name and path of the resource toml file
* The execute function is a qiskit defined function that turns this qiskit circuit into a qasm 'qobj' and then calls the run method described in this dax_backend.py file
* the run() method calls the qobj_to_dax() function, which is where the transpilation from qasm object to dax object happens.

### qiskit/providers/dax/qobj_to_dax.py
* This file contains all of the code to take the qobj and turn it into a scheduled dax program.
* Most feature changes will happen by modifying the code in this file

### qiskit/providers/dax/dax_job.py
* A job object is what is returned from the execute() function
* The DAX code is rendered from the jinja template onto the terminal as a method print_dax() on this object
* If we want to download this as a file as well or instead this is where that change would happen


### qiskit/providers/dax/dax_jinja.j2
* This is the template for what an outputted DAX program should look like. 
* The instructions that are gathered from the qiskit transpilation are placed inside the template

### tests/resources.toml
* The resources.toml is the file that describes what the hardware requirements are for each gate operation, and the overall capacaties of the machine
* The file name for the resources.toml is described in the circuit programs via the following two function calls
  * backend = dax.get_backend('dax_code_generator')
  * backend.load_config("resources.toml")

### tests/test_circuit_*.py
* Each of the test_circuit_* python files runs a different example, each showing off different capabilites or features of the qisdax compiler.


# Project Information

## Problem Statement
* This project is to develop a new provider and backend for Qiskit that uses the DAX language from Duke University to control the ion trap quantum computer.

### Ion Trap Computers
* Ion trap computers uses trapped ionized atoms as qubits.
* Sets, changes, and measures state via lasers.
* Each qubit can be coupled with the others in a chain
   * Hardware limitations allow up to 11 coupled pairs (IonQ)
   * 79 total single-qubits   
   * "Our native entangling gate is created by simultaneously 'plucking' two ions in on our chain with precise pulses of laser light. This creates vibrations in the ion chain which are dependent on the qubit state. Since the amount that qubits interact depends on their distance from each other, these different vibrations result in an interaction between the two qubits that depends on the qubit state. At the end of the operation, the vibrations are gone, and the ions are left entangled." (IonQ)

### ARTIQ
* ARTIQ is a framework for controling quantum devices.
* The DAX language is an interface to ARTIQ, and that is that we will generate from Qiskit to set up the physical ion-trap quantum computing device
* DAX is a Python package, which should allow for easy interfacing with other Python based languages or frameworks

### Qiskit
* Qiskit is a quantum programing language developed by IBM
* It is written in the high-level format of Python before being compiled to to qasm
* The qasm is then sent to the backend, traditionally either Aer, a simulator, or IBM's Quantum Computer IBMQ.
* Here is an example provider that allows use of AQT ion-trap quantum devices
  * https://github.com/qiskit-community/qiskit-aqt-provider
  * This system uses an AQT's API system, which is not something we have for Duke's, but it does provide good example of a minimum implementation

### Development Process
* We would implement a provider in Qiskit that interfaces with the DAX language which interfaces with the ARTIQ hardware system to create real circuits
* Different gates would have to be implemented in DAX
* We will use ISA example code from Duke in order to generate valid DAX code
* We may not be able to implement all of the gates that Qiskit, or Duke's ion-trap quantum computer supports


<!-- 
## Timeline
* 10/1 Receive the original project
* 10/8 Define first understanding of the problem statement
* 10/9 Meet with Duke
* 10/15 Establish detailed scope of project
* 10/29 Proof of concept 
* 11/12 Miminum Viable Product
* 11/19 All requirements met
* 11/27 Submit compiler and documentation -->


## References
* https://ionq.com/technology 
* http://dukespace.lib.duke.edu/dspace/bitstream/handle/10161/10461/Ahsan_duke_0066D_13028.pdf?sequence=1
* https://m-labs.hk/
* https://github.com/qiskit-community/qiskit-aqt-provider
* https://qiskit.org
* https://gitlab.com/duke-artiq
