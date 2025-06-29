""" scan songs that are missing lyrics, add the lyrics """

import mutagen
import os
import os.path
import whisper
import demucs
import logging

LOGGER=logging.getLogger(__name__)

class Context:
    def __init__(self, args):
        self.options = args
        self.model = whisper.load_model(args.model)

    def scan_file(self, path, root_dir):
        """ scan a file """
        name, ext = os.path.splitext(path)
        # TODO support other formats
        if ext != '.mp3':
            return

        outdir = os.path.join(self.options.output_dir,
            os.path.dirname(os.path.relpath(path, root_dir)))
        os.makedirs(outdir, exist_ok=True)
        LOGGER.debug("scanning %s", path)

        outfile = os.path.join(outdir, os.path.basename(name)) + '.txt'
        if os.path.isfile(outfile):
            LOGGER.debug("Lyric file %s already exists", outfile)
            return

        # TODO use mutagen to parse existing lyrics instead of using whisper

        lyrics = self.model.transcribe(path, verbose=True)
        lines = '\n'.join([seg.get('text','')
             for seg in lyrics.get('segments', [])])
        if lines:
            LOGGER.debug("Got %s lyrics:\n%s", lyrics.get('language'), lines)
        with open(outfile, 'w') as output:
            output.write(lines)

        # TODO optionally write lyrics in if so specified

    def scan_dir(self, basedir):
        """ scan a directory """
        LOGGER.info("Scanning directory %s", basedir)
        for root, dirs, files in os.walk(basedir):
            for name in files:
                self.scan_file(os.path.join(root, name), basedir)

