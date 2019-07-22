# -*- coding: utf-8 -*-
from odoo import exceptions


class ThrowException(exceptions.except_orm):
    def __init__(self, **kwargs):
        title = kwargs['title'] if 'title' in kwargs else "Error"
        message = kwargs['msg'] if 'msg' in kwargs else kwargs['message'] if 'message' in kwargs else "No Message"
        super(ThrowException, self).__init__(title, message)


class ThrowWarning:
    title = ""
    message = ""

    def __new__(cls, *args, **kwargs):
        cls.title = kwargs['title'] if 'title' in kwargs else "Warning"
        cls.message = kwargs['msg'] if 'msg' in kwargs else kwargs['message'] if 'message' in kwargs else "No Message"
        return cls.generate_warning()

    @classmethod
    def generate_warning(cls):
        return {
            'value': {},
            'warning': {
                'title': cls.title,
                'message': cls.message
            }
        }