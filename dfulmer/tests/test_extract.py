import pytest
from pymarc import MARCReader
from extract_bibs.extract import Extract

@pytest.fixture
def record():
    with open('dfulmer/tests/fixtures/onebib.mrc', 'rb') as fh:
       reader = MARCReader(fh)
       record = next(reader)
    return record

def test_initialize(record):
   extract = Extract(record)
   assert extract.bib.recid == '990186423140106381'

def test_has_008(record):
   extract = Extract(record)
   assert extract.has_008 == True

def test_has_008_false(record):
   for field in record.get_fields('008'):
      record.remove_field(field)
   extract = Extract(record)
   assert extract.has_008 == False

def test_process(record):
  extract = Extract(record)
  assert extract.process() == {"no 008 field": "0", "no arrival date": "0", "line": "SYSNUM:990186423140106381\tFMT:BK\tLANG:arm\tTITLE:Chʻspiatsʻats verkʻ : vep : hator aṛajin /\tAUTHOR:Alajajyan, Stepʻan,\tAUTHOR_TAG:100\tDATE:2019-\tTITLE_H:\tIMPRINT:Lusakn ; distributed by ATC Books International, Inc.,\tARRIVAL_DATE:2022-12-20\tISBN:9789939882567", "source of date": "260/4 subfield c"}

def test_process_without_008(record):
  for field in record.get_fields('008'):
      record.remove_field(field)
  extract = Extract(record)
  assert extract.process() == {"no 008 field": "1", "no arrival date": "0", "line": ""}

def test_process_without_arrival_date(record):
  record.remove_fields('974')
  extract = Extract(record)
  assert extract.process() == {"no 008 field": "0", "no arrival date": "1", "line": "SYSNUM:990186423140106381\tFMT:BK\tLANG:arm\tTITLE:Chʻspiatsʻats verkʻ : vep : hator aṛajin /\tAUTHOR:Alajajyan, Stepʻan,\tAUTHOR_TAG:100\tDATE:2019-\tTITLE_H:\tIMPRINT:Lusakn ; distributed by ATC Books International, Inc.,\tARRIVAL_DATE:\tISBN:9789939882567", "source of date": "260/4 subfield c"}
  