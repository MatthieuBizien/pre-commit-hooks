from __future__ import annotations

import os
import shutil

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
        ('not_pretty_formatted_xml.xml', 1),
        ('pretty_formatted_xml.xml', 0),
    ),
)
def test_unsorted_main(filename, expected_retval):
    ret = main([get_resource_path(filename)])
    assert ret == expected_retval


@pytest.mark.parametrize(
    ('filename', 'expected_retval'), (
        ('not_pretty_formatted_xml.xml', 1),
        ('pretty_formatted_xml.xml', 1),
        ('tab_pretty_formatted_xml.xml', 0),
    ),
)
def test_tab_main(filename, expected_retval):
    ret = main(['--indent', '\t', get_resource_path(filename)])
    assert ret == expected_retval


def test_autofix_main(tmpdir):
    srcfile = tmpdir.join('to_be_xml_formatted.xml')
    shutil.copyfile(
        get_resource_path('not_pretty_formatted_xml.xml'),
        str(srcfile),
    )

    # now launch the autofix on that file
    ret = main(['--autofix', str(srcfile)])
    # it should have formatted it
    assert ret == 1

    # file was formatted (shouldn't trigger linter again)
    ret = main([str(srcfile)])
    assert ret == 0


def test_invalid_main(tmpdir):
    srcfile1 = tmpdir.join('not_valid_xml.xml')
    srcfile1.write('<This> is not valid xml')
    srcfile2 = tmpdir.join('to_be_xml_formatted.xml')
    shutil.copyfile(
        get_resource_path('not_pretty_formatted_xml.xml'),
        str(srcfile2),
    )

    # it should have skipped the first file and formatted the second one
    assert main(['--autofix', str(srcfile1), str(srcfile2)]) == 1

    # confirm second file was formatted (shouldn't trigger linter again)
    assert main([str(srcfile2)]) == 0


@pytest.mark.xfail
def test_badfile_main():
    ret = main([get_resource_path('ok_yaml.yaml')])
    assert ret == 1


def test_diffing_output(capsys):
    resource_path = get_resource_path('not_pretty_formatted_xml.xml')
    expected_retval = 1
    a = os.path.join('a', resource_path)
    b = os.path.join('b', resource_path)
    expected_out = f'''\
--- {a}
+++ {b}
@@ -1,2 +1,3 @@
-<hello><world>!</world>
+<hello>
+    <world>!</world>
 </hello>
'''
    actual_retval = main([resource_path])
    actual_out, actual_err = capsys.readouterr()

    assert actual_retval == expected_retval
    assert actual_out == expected_out
    assert actual_err == ''
