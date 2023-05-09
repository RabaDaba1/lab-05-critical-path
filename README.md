# Lab 05 — Critical Path

The goal of this is lab is to implement a critical path algorithm.
On has also to build two simplex models finding the critical path duration.

Tasks:
* fill missing code in: 
  * [ ] `saport.critical_path.solvers.simplex_solver_min.py`
  * [ ] `saport.critical_path.solvers.simplex_solver_max.py`
  * [ ] `saport.critical_path.solvers.cpm_solver.py`

## SAPORT

SAPORT = Student's Attempt to Produce an Operation Research Toolkit

The project depends on the fairly recent numpy distribution and Python interpreter (version >= `3.9` is recommended). All depedendencies are listed in `requirements.txt`. One can install them with simple `pip install -r requirements.txt`, but using a virtual environment (e.g. virtualenv) is encouraged ([official tutorial](https://docs.python.org/3/tutorial/venv.html)). 

## Unit Tests

The `tests` folder contains unit tests written using `pytest`. 
Run it via `pytest`/`pycharm`/`vscode`.

## Functional Tests

The `example_input` folder contains some input instances. You may test your solvers by running: `python functional_test.py`.
This script is **not** used in the grading process.

## GitLab Setup 

* [ ] Make sure, you have a **private** group 
  * [how to create a group](https://docs.gitlab.com/ee/user/group/#create-a-group)
* [ ] Add @bobot-is-a-bot as the new group member (role: **maintainer**)
  * [how to add a group member](https://docs.gitlab.com/ee/user/group/#add-users-to-a-group)
* [ ] Fork this project into your new **private** group
  * [how to create a fork](https://docs.gitlab.com/ee/user/project/repository/forking_workflow.html#creating-a-fork)

## How To Submit Solutions

* [ ] Clone repository: git clone:
    ```bash 
    git clone <repository url>
    ```
* [ ] Solve the exercises 
    * remember to change only files with `#TODO` comments
* [ ] Commit your changes
    ```bash
    git add <path to the changed files>
    git commit -m <commit message>
    ```
* [ ] Push changes to the gitlab master branch
    ```bash
    git push -u origin master
    ```

The rest will be taken care of automatically. You can check the `GRADE.md` file for your grade / test results. Be aware that it may take some time (up to one hour) till this file appears / gets updated.  

## Repository Guide

```bash
.
├── README.md     # this README
├── conftest.py   # this file makes sure pytest works correctly :P
├── example_input # this folder contains some example inputs used in tests
│   ├── ...
│   └── project_03.txt # an input example
├── functional_test.py # script to run some functional tests
├── requirements.txt   # python libraries required by the problem
├── saport            
│   ├── critical_path  # folder with criticial path related code
│   │   ├── model.py   # straightforward representation of the problem
│   │   ├── project_network.py  # problem represented as a network (graph)
│   │   ├── solution.py         # representation of a solution
│   │   └── solvers
│   │       ├── cpm_solver.py # TODO: critical path algorithm
│   │       ├── networkx_solver.py # networkx based solver
│   │       ├── simplex_solver_max.py # TODO: simplex solver using "max" model
│   │       └── simplex_solver_min.py # TODO: simplex solver using "min" model
│   └── simplex # folder contains a simplex solver
└── tests 
```