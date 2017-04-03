# pylint: disable=invalid-name

import re
import time

import pytest
import requests
from requests.auth import HTTPDigestAuth


@pytest.mark.parametrize('extra_args', [[], ['--no-color']])
def test_output(turq_instance, extra_args):
    turq_instance.extra_args = extra_args
    with turq_instance:
        turq_instance.request('GET', '/foo/bar')
    output = turq_instance.console_output
    # pylint: disable=superfluous-parens
    assert ('mock on port %d' % turq_instance.mock_port) in output
    assert ('editor on port %d' % turq_instance.editor_port) in output
    assert 'new connection from' in output
    assert '> GET /foo/bar HTTP/1.1' in output
    assert '+ User-Agent: python-requests' not in output
    assert '< HTTP/1.1 404 Not Found' in output
    assert '+ Content-Type: text/plain; charset=utf-8' not in output


def test_verbose_output(turq_instance):
    turq_instance.extra_args = ['--verbose']
    with turq_instance:
        turq_instance.request('GET', '/foo/bar')
    output = turq_instance.console_output
    assert '+ User-Agent: python-requests' in output
    assert '+ Content-Type: text/plain; charset=utf-8' in output
    assert 'states:' in output


def test_editor(turq_instance):
    with turq_instance:
        resp = turq_instance.request_editor('GET', '/editor')
        assert resp.headers['Cache-Control'] == 'no-store'
        assert 'port %d' % turq_instance.mock_port in resp.text
        assert '>error(404)\n</textarea>' in resp.text
        assert 'with html() as document:' in resp.text      # from examples
        resp = turq_instance.request_editor('POST', '/editor',
                                            data={'rules': 'html()'})
        assert '>html()</textarea>' in resp.text
        resp = turq_instance.request('GET', '/')
        assert '<h1>Hello world!</h1>' in resp.text
    # Initial rules (``error(404)``) + the ones we posted
    assert turq_instance.console_output.count('new rules installed') == 2


def test_no_editor(turq_instance):
    turq_instance.extra_args = ['--no-editor']
    with turq_instance, pytest.raises(requests.exceptions.ConnectionError):
        turq_instance.request_editor('GET', '/editor')


def test_editor_bad_syntax(turq_instance):
    with turq_instance:
        resp = turq_instance.request_editor('POST', '/editor',
                                            data={'rules': 'html('})
        assert resp.status_code == 422
        assert resp.headers['Content-Type'] == 'text/plain; charset=utf-8'
        assert resp.text == 'unexpected EOF while parsing (<rules>, line 1)'


def test_editor_bad_form(turq_instance):
    with turq_instance:
        resp = turq_instance.request_editor('POST', '/editor',
                                            data={'foo': 'bar'})
        assert resp.status_code == 400
        assert resp.text == 'Bad form'


def test_editor_static(turq_instance):
    with turq_instance:
        resp = turq_instance.request_editor('GET', '/static/editor.css')
        assert resp.headers['Content-Type'] == 'text/css'
        assert 'font-size' in resp.text
        resp = turq_instance.request_editor(
            'GET', '/static/codemirror/lib/codemirror.js')
        assert resp.headers['Content-Type'] == 'application/javascript'


def test_debug_output(turq_instance):
    with turq_instance:
        turq_instance.request_editor('POST', '/editor',
                                     data={'rules': 'debug(); html()'})
        turq_instance.request('GET', '/')
    assert '+ User-Agent: python-requests' in turq_instance.console_output
    assert '+ Content-Type: text/html' in turq_instance.console_output
    assert 'states:' not in turq_instance.console_output


def test_uncaught_exception(turq_instance):
    turq_instance.host = 'wololo.invalid'
    turq_instance.wait = False
    with turq_instance:
        time.sleep(1)
    assert 'turq: error: ' in turq_instance.console_output


def test_uncaught_exception_traceback(turq_instance):
    turq_instance.host = 'wololo.invalid'
    turq_instance.extra_args = ['-v']
    turq_instance.wait = False
    with turq_instance:
        time.sleep(1)
    assert 'Traceback (most recent call last):' in turq_instance.console_output
    assert 'turq: error: ' not in turq_instance.console_output


def test_editor_password(turq_instance):
    turq_instance.password = 'wololo'
    with turq_instance:
        resp = turq_instance.request_editor(
            'POST', '/editor', data={'rules': 'html()'},
            auth=HTTPDigestAuth('', 'foobar'))
        assert resp.status_code == 401
        assert 'Hello world!' not in turq_instance.request('GET', '/').text
        resp = turq_instance.request_editor(
            'POST', '/editor', data={'rules': 'html()'},
            auth=HTTPDigestAuth('', 'wololo'))
        assert resp.status_code == 200
        assert 'Hello world!' in turq_instance.request('GET', '/').text


def test_editor_password_auto_generated(turq_instance):
    turq_instance.password = None
    with turq_instance:
        pass
    assert re.search(r'editor password: [A-Za-z0-9]{24}$',
                     turq_instance.console_output)
