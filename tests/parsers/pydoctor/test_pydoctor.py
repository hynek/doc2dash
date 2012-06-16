from mock import patch

from doc2dash.parsers import types
from doc2dash.parsers.pydoctor.parser import parse, _guess_type


def test_guess_type():
    ts = [
            ('startServer',
             'twisted.conch.test.test_cftp.CFTPClientTestBase.html#'
                'startServer',
             types.METHOD),
            ('A', 'twisted.test.myrebuilder1.A.html', types.CLASS),
            ('epollreactor', 'twisted.internet.epollreactor.html',
             types.PACKAGE)
    ]

    for t in ts:
        assert _guess_type(t[0], t[1]) == t[2]


EXAMPLE_PARSE_RESULT = [
        ('twisted.conch.insults.insults.ServerProtocol'
            '.ControlSequenceParser.A', types.METHOD,
         'twisted.conch.insults.insults.ServerProtocol'
            '.ControlSequenceParser.html#A'),
        ('twisted.test.myrebuilder1.A', types.CLASS,
         'twisted.test.myrebuilder1.A.html'),
        ('twisted.test.myrebuilder2.A', types.CLASS,
         'twisted.test.myrebuilder2.A.html'),
        ('twisted.test.test_jelly.A', types.CLASS,
         'twisted.test.test_jelly.A.html'),
        ('twisted.test.test_persisted.A', types.CLASS,
         'twisted.test.test_persisted.A.html'),
        ('twisted.test.myrebuilder1.A.a', types.METHOD,
         'twisted.test.myrebuilder1.A.html#a'),
        ('twisted.test.myrebuilder1.Inherit.a', types.METHOD,
         'twisted.test.myrebuilder1.Inherit.html#a'),
        ('twisted.test.myrebuilder2.A.a', types.METHOD,
         'twisted.test.myrebuilder2.A.html#a'),
        ('twisted.test.myrebuilder2.Inherit.a', types.METHOD,
         'twisted.test.myrebuilder2.Inherit.html#a'),
        ('twisted.web._newclient.HTTP11ClientProtocol.abort', types.METHOD,
         'twisted.web._newclient.HTTP11ClientProtocol.html#abort')
]


def test_parse():
    example = open('tests/parsers/pydoctor/pydoctor_example.html').read()
    with patch('builtins.open') as mock:
        mock.return_value = example
        assert list(parse('foo')) == EXAMPLE_PARSE_RESULT
