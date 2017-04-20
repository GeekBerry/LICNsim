#!/usr/bin/python3
#coding=utf-8

INF= 0x7FFFFFFF  # 无穷大 此处用4byte整形最大正数

# transfer_t 包发送状态
class TransferState:
    UNSEND, SENDING, ARRIVED, LOSS, DROP = 0,1,2,3,4
    TYPE_STRING= ['unsend', 'sending', 'arrived', 'loss', 'drop']
