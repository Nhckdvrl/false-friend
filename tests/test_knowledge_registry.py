"""Registry tests check integrity/provenance, not research quality from note length."""
import csv
from pathlib import Path

import pytest

from scripts.build_knowledge_index import FIELDS, load_registry, render_index, render_cards
from scripts.check_knowledge import coverage_missing
from scripts.query_knowledge import query_sources


def record(**changes):
    item = dict(id='P001', title='Test word sense paper', url='https://example.org/paper',
                stage='S3', domain='test', asset='catalogue/SOURCE_CARDS.md#p001',
                scope='Known abstract only; no detailed experiment claim.', origin='catalogue')
    item.update(changes)
    return item


def write_registry(root: Path, rows):
    path = root / 'knowledge/sources.tsv'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter='\t')
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_registry_and_explicit_bounded_cards(tmp_path):
    rows = load_registry(write_registry(tmp_path, [record()]))
    assert len(rows) == 1
    assert 'S3 / catalogue' in render_index(rows)
    cards = render_cards(rows)
    assert '<a id="p001"></a>' in cards
    assert 'Known abstract only' in cards


@pytest.mark.parametrize('rows, match', [
    ([record(), record()], 'duplicate'),
    ([record(stage='S9')], 'stage'),
    ([record(stage='S1')], 'catalogue-only'),
    ([record(asset='../external.md')], 'inside knowledge'),
    ([record(url='http://example.org')], 'HTTPS'),
])
def test_registry_rejects_unreliable_structure(tmp_path, rows, match):
    with pytest.raises(ValueError, match=match):
        load_registry(write_registry(tmp_path, rows))


def test_no_silent_loss_of_previous_index_sources():
    old = '| [A](https://example.org/paper/) | body |\n| [B](https://example.org/second) | x |'
    assert coverage_missing(old, [record()]) == ['https://example.org/second']
    assert coverage_missing(old, [record(), record(id='P002', url='https://example.org/second')]) == []


def test_shared_official_directory_url_is_allowed(tmp_path):
    rows = [record(), record(id='P002', title='Second title from same directory',
                             asset='catalogue/SOURCE_CARDS.md#p002')]
    assert len(load_registry(write_registry(tmp_path, rows))) == 2


def test_query_reports_scope_without_cross_card_leakage(tmp_path):
    rows = [record(), record(id='P002', title='Unrelated astronomy', scope='Different subject',
                             asset='catalogue/SOURCE_CARDS.md#p002')]
    write_registry(tmp_path, rows)
    card = tmp_path / 'knowledge/catalogue/SOURCE_CARDS.md'
    card.parent.mkdir()
    card.write_text(render_cards(rows), encoding='utf-8')
    hits = query_sources(tmp_path, 'word sense')
    assert [r['id'] for r in hits] == ['P001']
    assert hits[0]['stage'] == 'S3'
    with pytest.raises(ValueError):
        query_sources(tmp_path, '')
