from mock import patch

from doc2dash.parsers.pydoctor.parser import parse, _guess_type


def test_guess_type():
    types = [
            (
                'startServer',
                'twisted.conch.test.test_cftp.CFTPClientTestBase.html#'
                 'startServer',
                'clm'
            ),
            (
                'A',
                'twisted.test.myrebuilder1.A.html',
                'cl'
            ),
            (
                'epollreactor',
                'twisted.internet.epollreactor.html',
                'cat'
            )
    ]

    for t in types:
        assert _guess_type(t[0], t[1]) == t[2]


def test_parse():
    example = open('tests/parsers/pydoctor/pydoctor_example.html').read()
    with patch('builtins.open') as mock:
        mock.return_value = example
        assert (list(parse('foo')) == [
            ('A', 'clm', 'twisted.conch.insults.insults.ServerProtocol'
                '.ControlSequenceParser.html#A'),
            ('A', 'cl', 'twisted.test.myrebuilder1.A.html'),
            ('A', 'cl', 'twisted.test.myrebuilder2.A.html'),
            ('A', 'cl', 'twisted.test.test_jelly.A.html'),
            ('A', 'cl', 'twisted.test.test_persisted.A.html'),
            ('a', 'clm', 'twisted.test.myrebuilder1.A.html#a'),
            ('a', 'clm', 'twisted.test.myrebuilder1.Inherit.html#a'),
            ('a', 'clm', 'twisted.test.myrebuilder2.A.html#a'),
            ('a', 'clm', 'twisted.test.myrebuilder2.Inherit.html#a'),
            ('abort', 'clm', 'twisted.web._newclient.HTTP11ClientProtocol'
                '.html#abort')
        ])
