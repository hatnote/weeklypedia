
# Credit to Mark Williams for this
import argparse
from contextlib import closing
from collections import namedtuple
import xml.etree.cElementTree as ET
import mailbox
import tempfile
import uuid
import re


class mbox_readonlydir(mailbox.mbox):
    """\
    A subclass of mbox suitable for use with mboxs insides a read-only
    /var/mail directory.

    Deletes messages via truncation, in the manner of heirloom-mailx.

    The `maxmem` specifies the largest sized mailbox to attempt to
    copy into RAM.  Larger mailboxes will be copied incrementally
    which is more hazardous.

    NB: This can corrupt your mailbox!  Only use this if you know you
    need it.
    """

    def __init__(self, path, factory=None, create=True, maxmem=1024 * 1024):
        mailbox.mbox.__init__(self, path, factory, create)
        self.maxmem = maxmem

    def flush(self):
        """\
        Write any pending changes to disk.

        NB: This deletes messages via truncation, so if it fails
        halfway through it may corrupt your mailbox!  Use only if you
        must.
        """

        # Appending and basic assertions are the same as in mailbox.mbox.flush.
        if not self._pending:
            if self._pending_sync:
                # Messages have only been added, so syncing the file
                # is enough.
                mailbox._sync_flush(self._file)
                self._pending_sync = False
            return

        # In order to be writing anything out at all, self._toc must
        # already have been generated (and presumably has been modified
        # by adding or deleting an item).
        assert self._toc is not None

        # Check length of self._file; if it's changed, some other process
        # has modified the mailbox since we scanned it.
        self._file.seek(0, 2)
        cur_len = self._file.tell()
        if cur_len != self._file_length:
            raise mailbox.ExternalClashError('Size of mailbox file changed '
                                             '(expected %i, found %i)' %
                                             (self._file_length, cur_len))

        self._file.seek(0)

        # Truncation logic begins here.  Mostly the same except we
        # can use tempfile because we're not doing rename(2).
        with tempfile.TemporaryFile() as new_file:
            new_toc = {}
            self._pre_mailbox_hook(new_file)
            for key in sorted(self._toc.keys()):
                start, stop = self._toc[key]
                self._file.seek(start)
                self._pre_message_hook(new_file)
                new_start = new_file.tell()
                while True:
                    buffer = self._file.read(min(4096,
                                                 stop - self._file.tell()))
                    if buffer == '':
                        break
                    new_file.write(buffer)
                new_toc[key] = (new_start, new_file.tell())
                self._post_message_hook(new_file)
            self._file_length = new_file.tell()

            self._file.seek(0)
            new_file.seek(0)

            # Copy back our messages
            if self._file_length <= self.maxmem:
                self._file.write(new_file.read())
            else:
                while True:
                    buffer = new_file.read(4096)
                    if not buffer:
                        break
                    self._file.write(buffer)

            # Delete the rest.
            self._file.truncate()

        # Same wrap up.
        self._toc = new_toc
        self._pending = False
        self._pending_sync = False
        if self._locked:
            mailbox._lock_file(self._file, dotlock=False)


DEFAULT_SUBJECT_PARSER = re.compile(
    'Cron <(?P<user>[^@].+)@(?P<host>[^>].+)> (?P<command>.*)')
DEFAULT_SUBJECT_RENDERER = 'Cron <%(user)s@%(host)s> %(command)s'


MESSAGE_ID_PARSER = re.compile('<(?P<id>[^@]+)@(?P<host>[^>+]+)>')


class RSSItem(namedtuple('RSSItem', ['title', 'description', 'link',
                                     'lastBuildDate', 'pubDate', 'guid'])):

    @classmethod
    def fromemail(cls, email, excludes=('command',),
                  redacted='REDACTED',
                  parser=DEFAULT_SUBJECT_PARSER,
                  renderer=DEFAULT_SUBJECT_RENDERER):
        match = parser.match(email.get('subject'))
        if not match:
            raise ValueError("Unparseable subject")
        parsed = match.groupdict()

        for exclude in excludes:
            parsed[exclude] = redacted
        lastBuildDate = pubDate = email.get('date')
        title = renderer % parsed

        match = MESSAGE_ID_PARSER.match(email.get('message-id'))
        if not match:
            guid = uuid.uuid4()
        else:
            guid = match.group('id')

        return cls(title=title, description=None, link=None,
                   lastBuildDate=lastBuildDate, pubDate=pubDate, guid=guid)


def render_rss(rss_items):
    rss = ET.Element('rss', {'version': '2.0'})
    channel = ET.SubElement(rss, 'channel')
    for rss_item in rss_items:
        item = ET.SubElement(channel, 'item')
        for tag, text in rss_item._asdict().items():
            elem = ET.SubElement(item, tag)
            elem.text = text

    return ET.tostring(rss, encoding='UTF-8')


def lastn_emails(mb,
                 n,
                 parser=DEFAULT_SUBJECT_PARSER,
                 delete=True):
    emails = []
    for key in reversed(mb.keys()):
        if parser.match(mb[key].get('subject')):
            if len(emails) < n:
                emails.append(mb[key])
            elif delete:
                del mb[key]

    return emails


def rss_from_emails(path, maximum, delete=True):
    with closing(mbox_readonlydir(path)) as mb:
        emails = lastn_emails(mb, maximum, delete=delete)
        rendered = render_rss([RSSItem.fromemail(email)
                               for email in emails])

    return rendered


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mbox')
    parser.add_argument('--output', '-o', default=None)
    parser.add_argument('--maximum', '-m', type=int, default=256)
    parser.add_argument('--save', '-s', default=False,
                        action='store_true')
    args = parser.parse_args()

    rendered = rss_from_emails(args.mbox,
                               args.maximum,
                               delete=not args.save)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(rendered)
    else:
        print rendered


if __name__ == '__main__':
    main()
