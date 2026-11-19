const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { test } = require('node:test');

const html = fs.readFileSync(path.join(__dirname, '../index.html'), 'utf8');
const source = html.slice(html.indexOf('  function buildUrl() {'), html.indexOf('  // Wire filter inputs'));

function build(selected, fields = {}) {
  const context = {
    selected: new Set(selected),
    LOCATIONS: [{ slug: 'rathmines-dublin' }, { slug: 'ranelagh-dublin' }, { slug: 'rathgar-dublin' }],
    propertyTypes: new Set(['apartments']),
    facilities: new Set(),
    mediaTypes: new Set(),
    document: { getElementById: id => ({ value: fields[id] ?? ({ section: 'property-for-rent', sort: 'publishDateDesc' }[id] || '') }) },
  };
  return new URL(vm.runInNewContext(`${source}\nbuildUrl()`, context));
}

test('one district uses the path instead of an ignored location query', () => {
  const url = build(['rathmines-dublin']);
  assert.equal(url.pathname, '/property-for-rent/rathmines-dublin');
  assert.equal(url.searchParams.has('location'), false);
});

test('multiple districts retain repeated location parameters and filters', () => {
  const url = build(['rathmines-dublin', 'ranelagh-dublin'], { priceTo: '2500', bedsFrom: '2' });
  assert.equal(url.pathname, '/property-for-rent/ireland');
  assert.deepEqual(url.searchParams.getAll('location'), ['rathmines-dublin', 'ranelagh-dublin']);
  assert.equal(url.searchParams.get('rentalPrice_to'), '2500');
  assert.equal(url.searchParams.get('numBeds_from'), '2');
  assert.equal(url.searchParams.get('propertyType'), 'apartments');
});

test('all districts use the Dublin path without a long location query', () => {
  const url = build(['rathmines-dublin', 'ranelagh-dublin', 'rathgar-dublin']);
  assert.equal(url.pathname, '/property-for-rent/dublin');
  assert.equal(url.searchParams.has('location'), false);
});

test('sales use the same location routing with sale price filters', () => {
  const url = build(['rathmines-dublin'], { section: 'property-for-sale', priceTo: '500000' });
  assert.equal(url.pathname, '/property-for-sale/rathmines-dublin');
  assert.equal(url.searchParams.get('salePrice_to'), '500000');
  assert.equal(url.searchParams.has('rentalPrice_to'), false);
});

test('no districts keeps the nationwide URL', () => {
  assert.equal(build([]).pathname, '/property-for-rent/ireland');
});
