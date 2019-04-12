#  Knowledge Representation Qualitative Reasoning 
### Qualitative model of a container system 
During this project we build a qualitative reasoning algorithm that is able to reason about a simple physical system: a container that can be filled with water (e.g. via a tap) and emptied (e.g. via a drain). The algorithm is able to provide a state-graph, showing all possible behaviours of the system. Moreover, the algorithm is able to provide an insightful trace, helping the user understand why these behaviours can occur in the system. 

## Getting Started
### Prerequisites

- Graphviz `pip install graphviz`
---
 :exclamation:**important**:exclamation: Graphviz also needs to be installed on your system in order to run. 
 * For *Linux* install via terminal: `sudo apt-get install graphviz`
 * For *Windows* go to  `https://www.graphviz.org/download/` 
	 * Download  *Stable 2.38 Windows install packages*
	 * Set a PATH to the folder "bin" within the downloaded folder
		 * Example: `C:\Program Files (x86)\graphviz-2.38\bin`
---
### Installing

#### Clone

Clone this repository to your local machine:
- HTTPS `https://github.com/OscarLigthart/Knowledge-Representation.git`
-  SSH `git@github.com:OscarLigthart/Knowledge-Representation.git`

---
### USAGE

Open your terminal in the repository "Assignment2"

For the algorithm to run on the basic system use:
Type in your command window: `python waterflow.py`

For the algorithm to run on the extended system use:
Type in your command window: `python waterflow.py --extended "1"`

A state-graph will appear in the folder in the form of a .pdf file and the trace will be printed to the terminal.


:exclamation: If you encounter any problems during running, please contact us at: *oscar.ligthart@student.uva.nl*

---

## Built With

* <i> Language</i>: Python 3.6

## Authors
*Knowledge Representation (QR project teams 40)-  Vrije Universiteit Amsterdam*

| **Oscar Ligthart** | **Vanessa Botha** | 
| :---: |:---:| 
| ![Oscar](https://avatars1.githubusercontent.com/u/23171320?s=400&v=4) | ![Vanessa](https://avatars0.githubusercontent.com/u/31652336?s=200&v=4)|
| <a href="https://github.com/OscarLigthart" target="_blank">`https://github.com/OscarLigthart`</a> | <a href="https://github.com/VanessaBotha" target="_blank">`https://github.com/VanessaBotha`</a> | 
---

## License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)
- **[MIT license](http://opensource.org/licenses/mit-license.php)**
- Copyright 2019 © KR group 40

## Acknowledgments
- <a href="https://gist.github.com/fvcproductions/1bfc2d4aecb01a834b46" target="_blank">sampleREADME.md</a>. Copyright 2015 © <a href="http://fvcproductions.com" target="_blank">FVCproductions</a>.

