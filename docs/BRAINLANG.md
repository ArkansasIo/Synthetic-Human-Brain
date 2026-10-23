# BrainLang

BrainLang is the embedded scripting language for Synthetic-Human-Brain. It is
Lua-inspired in its compact syntax, but uses an explicitly object-oriented
programming model and adds domain statements for neural simulation.

## Design goals

1. Small dependency-free lexer/parser/runtime.
2. Familiar imperative syntax for experiments and automation.
3. Classes and objects for neurons, populations, regions, sensors and agents.
4. First-class functions for learning rules and experiment callbacks.
5. Explicit logic and arithmetic expressions.
6. Domain statements for brain populations and connectivity.
7. A syntax that can later be compiled to Python, C++, WASM or GPU kernels.

BrainLang is a simulation DSL; it is not a claim that biological neurons run
source code or that the language reproduces human cognition by itself.

## File extension

Recommended extension: `.brain`

## Variables

```brainlang
var learning_rate = 0.01
let threshold = -50
const MAX_NEURONS = 1000
```

## Types

The core runtime supports:

- `null`
- boolean
- integer
- floating-point number
- string
- object
- class
- function
- list/dictionary values supplied by host integrations

## Operators

Arithmetic:

```text
+  -  *  /  %
```

Comparison:

```text
==  !=  <  <=  >  >=
```

Logic:

```text
and  or  not
```

Unary:

```text
- x
! x
not x
```

## Functions

```brainlang
fn reward_error(reward, value, next_value) {
    return reward + 0.99 * next_value - value
}

var error = reward_error(1.0, 0.25, 0.8)
```

## Classes and objects

```brainlang
class Neuron {
    fn init(threshold) {
        this.threshold = threshold
    }

    fn should_fire(input) {
        if input >= this.threshold {
            return true
        } else {
            return false
        }
    }
}
```

The object model is designed to support future host-side classes such as:

```text
Neuron
Synapse
Population
BrainRegion
BrainNetwork
Stimulus
Sensor
MotorController
Memory
LearningRule
Experiment
Recorder
```

## Brain declarations

A brain is a simulation container:

```brainlang
brain Cortex {
    population Excitatory size 1000
    population Inhibitory size 250

    connect Excitatory -> Inhibitory weight 0.20 delay 1.5
    connect Inhibitory -> Excitatory weight -0.35 delay 2.0
}
```

The parser represents populations and connections as structured objects so a
future compiler can lower them into `BrainNetwork`, `NeuralPopulation`,
`BrainRegion`, and connectome objects.

## Conditional logic

```brainlang
if dopamine > 0.5 and reward > 0 {
    print("reinforce")
} else {
    print("do not reinforce")
}
```

## Loops

```brainlang
var x = 0
while x < 100 {
    x = x + 1
}
```

The current runtime includes a safety limit on `while` iterations.

## Simulation statements

The language reserves domain keywords for simulation control:

```brainlang
step 1.0
stimulus VisualInput 0.8
emit neuron_42
record spikes
```

The initial interpreter accepts `step` and reserves the remaining statements
for the host simulation API. This keeps the language grammar stable while the
simulation backend grows.

## Planned standard library

```text
brain.neuron
brain.synapse
brain.receptor
brain.population
brain.region
brain.connectome
brain.plasticity
brain.memory
brain.sensory
brain.motor
brain.reward
brain.statistics
brain.experiment
brain.io
brain.visualization
```

## Planned syntax extensions

### Object construction

```brainlang
var neuron = new Neuron(-50)
```

### Typed declarations

```brainlang
var rate: float = 20.0
var count: int = 100
```

### Interfaces

```brainlang
interface LearningRule {
    fn update(weight, pre, post)
}
```

### Events

```brainlang
on spike(neuron) {
    record neuron
}
```

### Parallel simulation

```brainlang
parallel population Cortex {
    step 0.1
}
```

### GPU/HPC execution hints

```brainlang
backend cuda
backend mpi
backend cpu
```

These extensions should be implemented only when the corresponding backend
semantics exist; they are language roadmap items rather than promises of
current functionality.

## Compiler architecture

```text
.brain source
     |
     v
   Lexer
     |
     v
   Parser
     |
     v
 Abstract Syntax Tree
     |
     +---- Interpreter
     |
     +---- Python backend
     |
     +---- C++ backend
     |
     +---- WASM backend
     |
     +---- CUDA/HPC backend
```

The language is intentionally separated from the scientific models. BrainLang
controls and composes models; it does not redefine the numerical equations
implemented by the Python simulation modules.
