const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file:///home/user/Sep2026/aster-mechanism-review/report.html', {waitUntil:'networkidle'});
  await p.pdf({path:'/home/user/Sep2026/aster-mechanism-review/人工星状体光致运动与产生力机理评析.pdf', format:'A4', printBackground:true, preferCSSPageSize:true,
    displayHeaderFooter:true, headerTemplate:'<div></div>',
    footerTemplate:'<div style="font-size:8px;color:#64748b;width:100%;text-align:center;font-family:WenQuanYi Zen Hei">人工星状体机理评析 · 第 <span class="pageNumber"></span> / <span class="totalPages"></span> 页</div>'});
  await b.close();
})();
