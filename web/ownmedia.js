// ownmedia.js: the quiz stills are files of this site. A page that does not know its own address (the preview, the plain build opened
// from disk) asks for them at the live address, so a test would depend on the network and on what is deployed. This wrapper makes every
// browser context answer those requests from ./media-out instead.   usage: const b = require('./ownmedia')(await chromium.launch());
const fs = require('fs'), path = require('path');
const LIVE = process.env.SITE_BASE || 'https://insanelukas.github.io/insanecoaching/';
module.exports = b => {
  const mk = b.newContext.bind(b);
  b.newContext = async o => {
    const ctx = await mk(o);
    await ctx.route(u => u.href.startsWith(LIVE + 'img/') || u.href.startsWith(LIVE + 'vid/'), r => {
      const f = path.join(__dirname, 'media-out', decodeURIComponent(r.request().url().slice(LIVE.length).split(/[?#]/)[0]));
      return fs.existsSync(f) ? r.fulfill({ status: 200, contentType: /\.mp4$/.test(f) ? 'video/mp4' : 'image/jpeg', body: fs.readFileSync(f) }) : r.fulfill({ status: 404, body: '' });
    });
    return ctx;
  };
  return b;
};
