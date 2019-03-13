#!/usr/bin/python
# -*- coding: utf-8 -*-
import pytest
import numpy as np
from brain.computation import StandardComputation
from brain.neurons import SimpleNeuronsFactory
from brain.sensor import Sensor
from brain.synapses import InputConnection
from brain.synapses import FeedbackConnection
from brain.synapses import InhibitionConnection


@pytest.fixture(scope='module')
def num_neurons():
    return 10

@pytest.fixture(scope='module')
def dummy_output(num_neurons):
    return np.random.rand(num_neurons) < 0.5

@pytest.fixture(scope='module')
def neuron_factory(num_neurons, dummy_output, dummy_computation):
    return SimpleNeuronsFactory(num_neurons, dummy_computation(dummy_output))

@pytest.fixture(scope='module')
def num_inputs():
    return 10

@pytest.fixture
def sensor_input(num_inputs):
    return np.random.rand(num_inputs)
# def test_self_inhibition_symmetry():
#     layer = neurons(3)
#     inhibitions = InhibitionConnection(layer)

#     assert np.allclose(inhibitions._mask, inhibitions._mask.T, atol=1e-8)

# def test_self_inhibition_non_reflective():
#     layer = neurons(3)
#     inhibitions = InhibitionConnection(layer)

#     assert np.all(np.diagonal(inhibitions._mask) == False)

def test_input_propagation_from_sensor(sensor_input, neuron_factory):
    sensor = Sensor(len(sensor_input))
    layer = neuron_factory()
    InputConnection(sensor, layer)

    sensor.emit(sensor_input)

    assert layer._inputs is not None
    assert np.all(layer._inputs.values == sensor_input)

def test_input_propagation_from_layer(dummy_output, neuron_factory):
    layer1 = neuron_factory()
    layer2 = neuron_factory()
    InputConnection(layer1, layer2)

    layer1.compute()

    assert layer2._inputs is not None
    assert np.all(layer2._inputs.values == dummy_output)

def test_inhibition_propagation(dummy_output, neuron_factory):
    layer1 = neuron_factory()
    layer2 = neuron_factory()
    InhibitionConnection(layer1, layer2)

    layer1.compute()

    assert layer2._inhibitions is not None
    assert np.all(layer2._inhibitions.values == dummy_output)

def test_feedback_propagation(dummy_output, neuron_factory):
    layer1 = neuron_factory()
    layer2 = neuron_factory()
    FeedbackConnection(layer1, layer2)

    layer1.compute()

    assert layer2._feedback is not None
    assert np.all(layer2._feedback.values == dummy_output)
