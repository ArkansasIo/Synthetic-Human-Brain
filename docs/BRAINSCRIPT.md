# BrainScript Language Specification

## Purpose

**BrainScript** is the domain-specific language for the Synthetic Human Brain project. It is designed to describe neural populations, connectivity, experiments, stimulation/recording intent, simulation control, and general program logic in a compact, readable syntax.

BrainScript is a computational research language. It does not imply that a program is a biological brain, consciousness, or a clinically validated model.

## File extension

BrainScript source files use `.brain`.

Example:

```brain
brain Cortex {
    population Excitatory size 100
    population Inhibitory size 25
    connect Excitatory -> Inhibitory weight 0.20 delay 1.5
}
```

## Core language

### Values

- integers
- floating-point numbers
- strings
- booleans: `true`, `false`
- `null`
- objects/classes

### Variables

```brain
var threshold = -50
const learning_rate = 0.01
```

### Functions

```brain
fn reward(value, target) {
    return target - value
}
```

### Classes

```brain
class Neuron {
    fn init(threshold) {
        this.threshold = threshold
    }

    fn fires(input) {
        if input >= this.threshold {
            return true
        }
        return false
    }
}
```

### Brain declarations

```brain
brain Hippocampus {
    population DentateGyrus size 1000
    population CA3 size 3000
    population CA1 size 3000
    connect DentateGyrus -> CA3 weight 0.35 delay 2.0
    connect CA3 -> CA1 weight 0.50 delay 2.5
}
```

### Control flow

Supported core forms include `if`, `else`, `while`, `return`, functions, and expressions.

### Simulation control

```brain
step 1.0
```

The value represents a model time increment whose physical units are defined by the host simulation configuration.

## Neural domain model

BrainScript will progressively expose these domain objects:

```text
Brain
Region
Area
Population
Neuron
Synapse
Connection
Stimulus
Recording
Experiment
Clock
Memory
MotorCommand
SensoryInput
Neuromodulator
```

## Planned statements

The language roadmap includes explicit forms for:

- `stimulate`
- `record`
- `emit`
- `observe`
- `connect`
- `disconnect`
- `plasticity`
- `experiment`
- `measure`
- `checkpoint`
- `replay`
- `backend`

These should compile to host APIs rather than directly controlling physical hardware.

## Runtime architecture

```text
.brain source
    |
    v
Lexer -> Parser -> AST -> Semantic validation
                       |
                       v
                BrainScript runtime
                       |
          +------------+-------------+
          |            |             |
       simulator     replay       CL1 adapter
          |            |             |
          +------------+-------------+
                       |
                 experiment data
```

The same BrainScript program should be usable with a deterministic software backend, recorded-data replay, or an approved external neural platform through an adapter.

## Compatibility

The repository previously called this language **BrainLang**. `src/synthetic_brain/brainscript.py` provides the canonical BrainScript import surface while retaining compatibility with the existing implementation during migration.

Migration rule:

```python
from synthetic_brain.brainscript import BrainRuntime
```

New examples and documentation should use BrainScript terminology. Existing BrainLang imports may remain temporarily for backwards compatibility.

## Safety boundary

BrainScript is not a medical device programming language. Stimulation commands must pass through hardware-specific validation, isolation, authorization, and safety layers. The language itself should not contain assumptions that make arbitrary electrical stimulation safe for biological tissue.
