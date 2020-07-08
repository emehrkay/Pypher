#!/usr/bin/env python
"""
Horizontal split example.
"""
from __future__ import unicode_literals

import json

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import HSplit, Window, Float, FloatContainer
from prompt_toolkit.layout.controls import FormattedTextControl, BufferControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import Frame


edit_buffer = Buffer()
edit_buffer.text = ''

mid_buffer = Buffer()
lower_buffer = Buffer()


from pypher import Pypher, builder, create_function, create_statement
from pypher.builder import __


builder.CHECK_CUSTOM_CLASHES = False


def input(_):
    try:
        p = Pypher()

        cmd = (
            '{text} \n'
            'q = str(p) \n'
            'params = p.bound_params \n'
            'mid_buffer.text = q \n'
            'lower_buffer.text = json.dumps(params) '
        ).format(text=edit_buffer.text)
        exec(cmd)
    except Exception as e:
        mid_buffer.text = 'There is an error in your Pypher cell'
        lower_buffer.text = str(e)


edit_buffer.on_text_changed += input
toolbar_message = ('[Ctrl] + q (to quit)'
    ' | [Ctrl] + u (to clear)')
msg = (' Pypher, __, create_function, and create_statement are imported'
    ' | p is a Pypher instance')
pyper_message = (msg)
kb = KeyBindings()


body = HSplit([
    Window(FormattedTextControl(pyper_message), height=1, style='reverse'),
    Window(height=1, char=''),

    FloatContainer(
        content=Window(BufferControl(buffer=edit_buffer), wrap_lines=True),
        floats=[
            Float(
                Frame(Window(FormattedTextControl(' Pypher '))),
                right=0, bottom=0),
        ]),
    FloatContainer(
        content=Window(BufferControl(buffer=mid_buffer), wrap_lines=True),
        floats=[
            Float(
                Frame(Window(FormattedTextControl(' Cypher ')),
                       style='bg:#AB505D #ffffff'),
                right=0, bottom=0),
        ], style='bg:#AB505D'),
    FloatContainer(
        content=Window(BufferControl(buffer=lower_buffer), wrap_lines=True),
        floats=[
            Float(
                Frame(Window(FormattedTextControl(' Params ')),
                style='bg:#222'),
                    right=0, bottom=0),
        ], style='bg:#222'),
    Window(FormattedTextControl(toolbar_message), height=1, style='reverse'),
], padding=0)


@kb.add('c-q')
def _(event):
    " Quit application. "
    event.app.exit()


@kb.add('c-u')
def _(event):
    " Clear Pypher "
    edit_buffer.text = ''


application = Application(
    layout=Layout(body),
    key_bindings=kb,
    full_screen=True)


def run():
    application.run()


if __name__ == '__main__':
    run()
