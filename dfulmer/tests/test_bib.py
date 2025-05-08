import pytest
from pymarc import MARCReader, Field, Subfield
from extract_bibs.extract import Bib

@pytest.fixture
def record():
    with open('dfulmer/tests/fixtures/onebib.mrc', 'rb') as fh:
       reader = MARCReader(fh)
       record = next(reader)
    return record

def test_recid(record):
   bib = Bib(record)
   assert bib.recid == '990186423140106381'

def test_has_008_is_true(record):
   bib = Bib(record)
   assert bib.has_008 == True

def test_has_008_is_false(record):
   for field in record.get_fields('008'):
      record.remove_field(field)
   bib = Bib(record)
   assert bib.has_008 == False

def test_f008_lang(record):
   bib = Bib(record)
   assert bib.f008_lang == 'arm'

def test_f008_lang_without_008(record):
   for field in record.get_fields('008'):
      record.remove_field(field)
   bib = Bib(record)
   assert bib.f008_lang == ''

def test_title_ab(record):
   bib = Bib(record)
   assert bib.title_ab == 'Chʻspiatsʻats verkʻ : vep : hator aṛajin /'

def test_author_and_tag(record):
   bib = Bib(record)
   assert bib.author_and_tag == ['Alajajyan, Stepʻan,', '100']

def test_pub_date(record):
   bib = Bib(record)
   assert bib.pub_date[0] == '2019-'

def test_pub_date_source(record):
   bib = Bib(record)
   assert bib.pub_date[1] == '260/4 subfield c'

def test_pub_date_without_260(record):
   record.remove_fields('260')
   bib = Bib(record)
   assert bib.pub_date[0] == '2019'

def test_pub_date_source_without_260(record):
   record.remove_fields('260')
   bib = Bib(record)
   assert bib.pub_date[1] == 'date from 008'

@pytest.mark.parametrize(
    "test_input,expected",
    [(str(year), str(year)) for year in range(1990, 2011)]
)
def test_pub_date_source_without_different_years(record, test_input, expected):
    record.remove_fields('260')
    record.add_field(
        Field(
            tag='260',
            indicators=[' ', ' '],
            subfields=[Subfield(code='c', value=test_input)]
        )
    )
    bib = Bib(record)
    assert bib.pub_date[0] == expected

def test_pub_date_source_with_printout(record):
   record.remove_fields('260')
   record.add_field(
      Field(
         tag='260',
         indicators=[' ', ' '],
         subfields=[Subfield(code='a', value='Beograd, 10. i 11. oktobar 2001. god.. - <S. l. : s.n.>, 2001.')]
         )
   )
   bib = Bib(record)
   assert bib.pub_date == ['', '260/4 unknown multiple dates in from text', '990186423140106381: Beograd, 10. i 11. oktobar 2001. god.. - <S. l. : s.n.>, 2001.: 2001, 2001']

def test_title_h(record):
   bib = Bib(record)
   assert bib.title_h == ''

def test_title_h_with_h(record):
   field_245 = record.get_fields('245')
   field_245 = field_245[0]
   field_245.add_subfield('h', 'This is the h')
   bib = Bib(record)
   assert bib.title_h == 'This is the h'

def test_imprint(record):
   bib = Bib(record)
   assert bib.imprint == 'Lusakn ; distributed by ATC Books International, Inc.,'

def test_arrival_date(record):
   bib = Bib(record)
   assert bib.arrival_date == ['2022-12-20', '0', '990186423140106381: 2 arrival dates in record: 2022-03-11, 2022-12-20']

def test_arrival_date_lacking(record):
   record.remove_fields('974')
   bib = Bib(record)
   assert bib.arrival_date == ['', '1', '']

def test_search_keys(record):
   bib = Bib(record)
   assert bib.search_keys == '	ISBN:9789939882567'

def test_search_keys_with_oclc_number(record):
   record.add_field(
        Field(
            tag='035',
            indicators=[' ', ' '],
            subfields=[Subfield(code='a', value='(OCoLC)on1082869878')]
        )
    )
   bib = Bib(record)
   assert bib.search_keys == '	ISBN:9789939882567	OCLC:1082869878'