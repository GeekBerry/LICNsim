#!/usr/bin/python3
#coding=utf-8

from debug import showCall

from visualizer.common import SpinBox, CheckBox, ComboBox, DoubleSpinBox


# ----------------------------------------------------------------------------------------------------------------------
def ctrlContentStoreUnit(tree_item, cs_unit):
    tree_item['size'].setTexts( len(cs_unit) )
    tree_item['capacity'].setWidgets(SpinBox(cs_unit, 'capacity'))

@showCall
def ctrlNodeBufferUnit(tree_item, buffer_unit):
    tree_item['size'].setWidgets(SpinBox(buffer_unit, 'buffer_size'))
    tree_item['rate'].setWidgets(SpinBox(buffer_unit, 'rate'))

    tree_item['buffer'].clear()
    tree_item['buffer'].setTexts( len(buffer_unit._bucket) )
    for row, each in enumerate(buffer_unit._bucket):
        tree_item['buffer'][row].setTexts( each )


def ctrlInfoUnit(tree_item, buffer_unit):
    tree_item['max_size'].setWidgets( SpinBox(buffer_unit, 'max_size') )
    tree_item['life_time'].setWidgets( SpinBox(buffer_unit, 'life_time') )


def ctrlFaceUnit(tree_item, face_unit):
    for faceid, face in face_unit.table.items():
        tree_item[faceid]['can_recv'].setWidgets(CheckBox(face, 'can_recv'))
        tree_item[faceid]['can_send'].setWidgets(CheckBox(face, 'can_send'))


import constants
def ctrlPolicyUnit(tree_item, policy_unit):
    box= ComboBox(policy_unit, 'PolicyType', constants.POLICY_LIST)
    tree_item['PolicyType'].setWidgets(box)


def ctrlChannel(tree_item, channel):
    tree_item['rate'].setWidgets( SpinBox(channel, 'rate') )
    tree_item['buffer_size'].setWidgets( SpinBox(channel, 'buffer_size') )
    tree_item['delay'].setWidgets( SpinBox(channel, 'delay') )
    tree_item['loss'].setWidgets( DoubleSpinBox(channel, 'loss') )

    tree_item['buffer'].clear()
    tree_item['buffer'].setTexts( len(channel._bucket) )
    for row, each in enumerate(channel._bucket):
        tree_item['buffer'][row].setTexts( each )

# ======================================================================================================================
from core.face import FaceUnit
from core.info_table import InfoUnit
from core.cs import ContentStoreUnit
from core.node import NodeBufferUnit
from core.policy import PolicyUnit
from core.channel import Channel

MODULE_CONTROLLER_MAP= {
    ContentStoreUnit:   ctrlContentStoreUnit,
    NodeBufferUnit:     ctrlNodeBufferUnit,
    InfoUnit:           ctrlInfoUnit,
    FaceUnit:           ctrlFaceUnit,
    PolicyUnit:         ctrlPolicyUnit,
    Channel:            ctrlChannel,
}

def bindModuleController(tree_item, unit):
    for module, controller in MODULE_CONTROLLER_MAP.items():
        if isinstance(unit, module):
            controller(tree_item, unit)
            return True
    return False
