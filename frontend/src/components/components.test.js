import {after, beforeEach, test} from 'node:test';
import assert from 'node:assert/strict';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {createServer} from 'vite';

const server = await createServer({server:{middlewareMode:true}, appType:'custom'});
after(() => server.close());
const {default: DeviceList} = await server.ssrLoadModule('/src/components/DeviceList.jsx');
const {default: DeviceForm} = await server.ssrLoadModule('/src/components/DeviceForm.jsx');
const i18n = await server.ssrLoadModule('/src/i18n/index.js');
beforeEach(() => i18n.setLocale('en', {}));
const props = {devices:[], loading:false,error:'',checking:new Set(),checkErrors:{},cooldowns:{}};

test('empty list offers adding a device', () => {
  assert.match(renderToStaticMarkup(React.createElement(DeviceList,props)), /No devices yet/);
});
test('forbidden target cannot be checked and has explanation', () => {
  const html=renderToStaticMarkup(React.createElement(DeviceList,{...props,devices:[{id:1,name:'Router',address:'router',status:'unknown',latency_ms:null,last_checked_at:null}]}));
  assert.match(html, /disabled/); assert.match(html,/only for 127.0.0.1/); assert.match(html,/No data/);
});
test('renders checking, offline status and zero latency', () => {
  const html=renderToStaticMarkup(React.createElement(DeviceList,{...props,checking:new Set([1]),devices:[{id:1,name:'Local',address:'127.0.0.1',status:'offline',latency_ms:0,last_checked_at:null}]}));
  assert.match(html,/Checking…/); assert.match(html,/status-offline/); assert.match(html,/0 ms/);
});
test('form has English labels and associated fields', () => {
  const html=renderToStaticMarkup(React.createElement(DeviceForm,{onCreated:()=>{}}));
  assert.match(html,/Add device/); assert.match(html,/for="device-name"/); assert.doesNotMatch(html,/[\u0400-\u04ff]/);
});


for (const language of ['en','de','ru']) {
  test(`form and visible errors render in ${language}`, () => {
    i18n.setLocale(language, {});
    try {
      const html=renderToStaticMarkup(React.createElement(DeviceForm,{onCreated:()=>{}}));
      assert.ok(html.includes(i18n.t('addHeading')));
      const list=renderToStaticMarkup(React.createElement(DeviceList,{...props,error:{code:'network_error'}}));
      assert.ok(list.includes(i18n.t('network_error')));
    } finally { i18n.setLocale('en', {}); }
  });
}
