#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Module for handling MiniColumns.

MiniColumns are a grouping of neurons that are connected to the same inputs.
"""
import json
import numpy as np
from brain.event import Event
from brain.neuron import Neuron, SimpleNeuronFactory
from util.factory import Factory, ConstantFactory


class MiniColumn:
    """A collection of Neurons connected to the same input."""

    def __init__(self, neurons):
        """Initializes the minicolumn."""
        assert len(neurons) > 0
        synapses = neurons[0].num_synapses
        assert all(n.num_synapses == synapses
                   for n in neurons)

        self._neurons = neurons
        self._num_synapses = synapses
        self._spike = Event()
        self._active = False
        self._inputs = np.zeros(synapses)
        self._allocate_input = [self._allocation_function(i)
                                for i in range(synapses)]
        self._outputs = np.zeros(len(neurons))

    def process(self):
        """Compute the value for this minicolumn and conditionally spike."""
        self._outputs = np.asarray([
            neuron.compute(self._inputs)
            for neuron in self._neurons
        ])
        self.active = any(self._outputs)

    def connect(self, other_mini_columns):
        """Create connections to the outputs of other minicolumns."""
        sampled_mini_columns = np.random.choice(
            other_mini_columns,
            size=self.num_synapses,
            replace=False
        )
        for i, mini_column in enumerate(sampled_mini_columns):
            mini_column.spike.subscribe(self._allocate_input[i])

    @property
    def active(self):
        """Whether the minicolumn is active."""
        return self._active

    @active.setter
    def active(self, new_value):
        """The active value, when changed, will trigger a spike event."""
        if self._active != new_value:
            self.spike(float(new_value))
        self._active = new_value

    @property
    def num_synapses(self):
        """The number of synapses per neuron."""
        return self._num_synapses

    @property
    def num_neurons(self):
        """The number of neurons in this minicolumn."""
        return len(self._neurons)

    @property
    def outputs(self):
        """Get the last-computed outputs."""
        return self._outputs

    @property
    def spike(self):
        """The spike event to subscribe to."""
        return self._spike

    def _allocation_function(self, i):
        """Helper function to create a lambda to set the ith input."""
        return lambda value: self._set_input(i, value)

    def _set_input(self, i, value):
        """Helper function to set the ith input to a given value."""
        self._inputs[i] = value

    def __str__(self):
        """The string representation of a mini column."""
        return "%s: %s" % (self.__class__, json.dumps({
            "inputs": str(self._inputs.astype(np.int32)),
            "activations": str(self._outputs.astype(np.int32))
            }, indent=4))


class MiniColumnFactory(Factory):
    """A Factory class for MiniColumns."""

    def __init__(self, num_neurons_factory, neuron_factory):
        """Initialize the factory."""
        self._num_neurons_factory = num_neurons_factory
        self._neuron_factory = neuron_factory

    def create(self):
        """Create a new minicolumn."""
        num_neurons = self._num_neurons_factory()
        neurons = [self._neuron_factory()
                   for _ in range(num_neurons)]
        return MiniColumn(neurons)


class SimpleMiniColumnFactory(MiniColumnFactory):
    """A simple factory class for MiniColumns."""

    def __init__(self,
                 num_neurons,
                 num_synapses,
                 neuron_threshold=0.5,
                 synapse_threshold=0.5):
        """Initialize the factory."""
        num_neurons_factory = ConstantFactory(num_neurons)
        neurons_factory = SimpleNeuronFactory(
            num_synapses, neuron_threshold, synapse_threshold)

        super().__init__(num_neurons_factory, neurons_factory)
