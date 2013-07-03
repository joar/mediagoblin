# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2011, 2012 MediaGoblin contributors.  See AUTHORS.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gobject
import gst
import gst.pbutils
import logging
from datetime import timedelta


logging.basicConfig()

_log = logging.getLogger(__name__)
_log.setLevel(logging.DEBUG)

class Discoverer(object):
    def __init__(self, timeout=5):
        self.discoverer = gst.pbutils.Discoverer(timeout * gst.SECOND)

        self.discoverer.connect('discovered', self._on_discovered)
        self.discoverer.connect('finished', self._on_finished)
        self.discoverer.connect('starting', self._on_starting)

        self.loop = gobject.MainLoop()

    def discover(self, uri):
        _log.info('Discovering {0}'.format(uri))

        self.discoverer.start()

        self.discoverer.discover_uri_async(uri)

        self.result = {}

        self.loop.run()

        # Once the loop is done, return the collected data
        return self.result

    def _on_starting(self, *args):
        _log.info('Discoverer starting')
        _log.debug(args)

    def _on_finished(self, *args):
        _log.info('Finished')
        _log.debug(args)
        self.loop.quit()

    def _on_discovered(self, _disc, info, error):
        _log.info('Discovered')

        uri = info.get_uri()
        result = info.get_result()

        errors = []

        if result == gst.pbutils.DISCOVERER_URI_INVALID:
            errors.append('Invalid URI: {0}'.format(uri))
        elif result == gst.pbutils.DISCOVERER_ERROR:
            errors.append('Discoverer error: {0}'.format(error.message))
        elif result == gst.pbutils.DISCOVERER_TIMEOUT:
            errors.append('Timeout')
        elif result == gst.pbutils.DISCOVERER_BUSY:
            errors.append('Discoverer busy')
        elif result == gst.pbutils.DISCOVERER_MISSING_PLUGINS:
            errors.append('Missing plugins: {0}'.format(
                info.get_misc().to_string()))
        elif result == gst.pbutils.DISCOVERER_OK:
            self.result.update(dict(
                duration=timedelta(
                    seconds=info.get_duration() // gst.SECOND),
                seekable=info.get_seekable(),
                tags=dict(info.get_tags()),
                streams=self._unwrap_streams(info.get_stream_info())))

        _log.debug('Got result {0}'.format(self.result))

    def _unwrap_streams(self, stream_info):
        streams = {}
        for stream in stream_info.get_streams():
            _d = dict(
                nick=stream.get_stream_type_nick(),
                caps=stream.get_caps().to_string(),
                bitrate=stream.get_bitrate(),
                tags=dict(stream.get_tags())
            )

            for i in range(0, 64):
                if not _d.get('nick'):
                    break

                stream_name = ''.join([
                    _d.get('nick'),
                    str(i)])
                if not stream_name in streams.keys():
                    streams.update({stream_name: _d})
                    break

        return streams


if __name__ == '__main__':
    d = Discoverer()
    #d.discover('file:///home/joar/test-video.webm')
    import pprint
    pp = pprint.PrettyPrinter(indent=4)

    result = d.discover(
        'http://docs.gstreamer.com/media/sintel_trailer-480p.webm')

    pp.pprint(result)

