from dbus_next import Variant
from .mpris import setup_mpris
from .playerctl import PlayerctlCli

import pytest

# TODO: test missing function does not segv


@pytest.mark.asyncio
async def test_format(bus_address):
    [mpris] = await setup_mpris('format-test', bus_address=bus_address)
    TITLE = 'A Title'
    ARTIST = 'An Artist'
    mpris.metadata = {
        'xesam:title': Variant('s', TITLE),
        'xesam:artist': Variant('as', [ARTIST]),
        'xesam:escapeme': Variant('s', '<hi>'),
        'mpris:length': Variant('x', 100000)
    }
    await mpris.ping()

    playerctl = PlayerctlCli(bus_address)

    cmd = await playerctl.run('metadata --format "{{artist}} - {{title}}"')
    assert cmd.stdout == f'{ARTIST} - {TITLE}', cmd.stderr

    cmd = await playerctl.run(
        'metadata --format "{{markup_escape(xesam:escapeme)}}"')
    assert cmd.stdout == '&lt;hi&gt;', cmd.stderr

    cmd = await playerctl.run('metadata --format "{{lc(artist)}}"')
    assert cmd.stdout == ARTIST.lower(), cmd.stderr

    cmd = await playerctl.run('metadata --format "{{uc(title)}}"')
    assert cmd.stdout == TITLE.upper(), cmd.stderr

    cmd = await playerctl.run('metadata --format "{{uc(lc(title))}}"')
    assert cmd.stdout == TITLE.upper(), cmd.stderr

    cmd = await playerctl.run('metadata --format \'{{uc("Hi")}}\'')
    assert cmd.stdout == "HI", cmd.stderr

    cmd = await playerctl.run('metadata --format "{{mpris:length}}"')
    assert cmd.stdout == "100000", cmd.stderr

    cmd = await playerctl.run(
        'metadata --format \'@{{ uc( "hi" ) }} - {{uc( lc( "HO"  ) ) }} . {{lc( uc(  title ) )   }}@\''
    )
    assert cmd.stdout == '@HI - HO . a title@', cmd.stderr

    cmd = await playerctl.run(
        'metadata --format \'{{default(xesam:missing, artist)}}\'')
    assert cmd.stdout == ARTIST, cmd.stderr

    cmd = await playerctl.run(
        'metadata --format \'{{default(title, artist)}}\'')
    assert cmd.stdout == TITLE, cmd.stderr

    cmd = await playerctl.run('metadata --format \'{{default("", "ok")}}\'')
    assert cmd.stdout == 'ok', cmd.stderr

    cmd = await playerctl.run('metadata --format \'{{default("ok", "not")}}\'')
    assert cmd.stdout == 'ok', cmd.stderr

    mpris.disconnect()
