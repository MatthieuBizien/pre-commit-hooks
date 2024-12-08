from __future__ import annotations

import pytest

from pre_commit_hooks.pretty_format_xml import main
from pre_commit_hooks.pretty_format_xml import pretty_format_xml
from testing.util import get_resource_path


def test_simple_xml():
    input_xml = '<root><child><subchild>value</subchild></child></root>'
    result = pretty_format_xml(input_xml, 4)
    expected = (
        """<root>
    <child>
        <subchild>value</subchild>
    </child>
</root>"""
    )
    assert result == expected


def test_self_closing_tags():
    input_xml = '<root><child /><child>text</child></root>'
    result = pretty_format_xml(input_xml, 2)
    expected = (
        """<root>
  <child />
  <child>text</child>
</root>"""
    )
    assert result == expected


def test_comments():
    input_xml = '<!-- Comment --><root><child>text</child></root>'
    result = pretty_format_xml(input_xml, 2)
    expected = (
        """<!-- Comment -->
<root>
  <child>text</child>
</root>"""
    )
    assert result == expected


def test_cdata():
    input_xml = (
        '<root><![CDATA[some <xml> content]]>'
        '<child>text</child></root>'
    )
    result = pretty_format_xml(input_xml, 2)
    expected = (
        """<root>
  <![CDATA[some <xml> content]]>
  <child>text</child>
</root>"""
    )
    assert result == expected


def test_namespaces():
    input_xml = (
        '<root xmlns:x="http://example.com">'
        '<x:child>namespaced</x:child></root>'
    )
    result = pretty_format_xml(input_xml, 2)
    expected = (
        """<root
  xmlns:x=\"http://example.com\">
  <x:child>namespaced</x:child>
</root>"""
    )
    assert result == expected


def test_doctype():
    input_xml = '<!DOCTYPE html><html><body><h1>Hello</h1></body></html>'
    result = pretty_format_xml(input_xml, 2)
    expected = (
        """<!DOCTYPE html>
<html>
  <body>
    <h1>Hello</h1>
  </body>
</html>"""
    )
    assert result == expected


@pytest.mark.parametrize(
    ('filename', 'expected_retval'), (
        ('pretty_formatted_xml.xml', 0),
    ),
)
def test_unsorted_main(filename, expected_retval):
    ret = main([get_resource_path(filename)])
    assert ret == expected_retval
