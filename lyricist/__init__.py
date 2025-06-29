""" scan songs that are missing lyrics, add the lyrics """

import mutagen
import os
import os.path
import whisper
import demucs.separate
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

        outfile = os.path.join(outdir, os.path.basename(name)) + '.txt'
        if os.path.isfile(outfile):
            LOGGER.info("Lyric file %s already exists", outfile)
            return

        LOGGER.info("scanning %s -> %s", path, outfile)

        # TODO use mutagen to parse existing lyrics instead of using whisper

        if self.options.demucs:
            try:
                path = self.extract_vocals(path, outdir)
                LOGGER.debug("Extracted vocals to %s", path)
            except Exception as e:
                LOGGER.exception("Error extracting vocals from %s: %s", path, e)

        try:
            lyrics = self.extract_lyrics(path)
            LOGGER.debug('Saving lyrics to %s', outfile)
            with open(outfile, 'w') as output:
                output.write(lyrics)
                output.write('\n')
        except Exception as e:
            LOGGER.exception("Error extracting lyrics from %s: %s", path, e)

        # TODO optionally write lyrics to id3 tag if so specified

    def extract_vocals(self, path, outdir):
        demucs.separate.main(['--mp3',
            '--two-stems', 'vocals',
            path,
            '-n', 'htdemucs',
            '-o', outdir,
            '--filename', '{stem}.{ext}'])

        return os.path.join(outdir, 'htdemucs', 'vocals.mp3')


    def extract_lyrics(self, path):
        lyrics = self.model.transcribe(path, verbose=self.options.verbosity > 1)
        lines = '\n'.join([seg.get('text','')
             for seg in lyrics.get('segments', [])])
        if lines:
            LOGGER.debug("Got %s lyrics:\n%s", lyrics.get('language'), lines)
        return lines


    def scan_dir(self, basedir):
        """ scan a directory """
        LOGGER.info("Scanning directory %s", basedir)
        for root, dirs, files in os.walk(basedir):
            for name in files:
                self.scan_file(os.path.join(root, name), basedir)

