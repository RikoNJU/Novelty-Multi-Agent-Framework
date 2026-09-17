const { chromium } = require('/home/lya3106643285/projects/Novelty-Multi-Agent-Framework/frontend/node_modules/@playwright/test');
const fs = require('fs');
const crypto = require('crypto');
const path = require('path');
const root = '/home/lya3106643285/projects/Novelty-Multi-Agent-Framework';
const out = path.join(root, 'docs/experiments/20260918_frontend_fullflow_acceptance/run');
const url = 'http://127.0.0.1:8010';
const pdf = path.join(root, 'examples/MG19333vrw.pdf');
const state = {mode:'A_pdf_upload', started_at:new Date().toISOString(), input_sha256:crypto.createHash('sha256').update(fs.readFileSync(pdf)).digest('hex'), posts:[], snapshots:[], page_errors:[], console_errors:[], run_id:null, refresh_count:0, report:null};
function save(){fs.writeFileSync(path.join(out,'live-browser-observation.json'),JSON.stringify(state,null,2)+'\n')}
function note(event, extra={}){const row={at:new Date().toISOString(),event,...extra};fs.appendFileSync(path.join(out,'browser-events.jsonl'),JSON.stringify(row)+'\n');process.stdout.write(JSON.stringify(row)+'\n')}
(async()=>{
 fs.mkdirSync(out,{recursive:true});save();
 const browser=await chromium.launch({headless:true,executablePath:'/home/lya3106643285/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome'});
 const page=await browser.newPage({viewport:{width:1440,height:900},acceptDownloads:true});
 page.on('request',req=>{if(req.method()==='POST'){state.posts.push({at:new Date().toISOString(),url:req.url()});save();note('business_post_sent',{count:state.posts.length})}});
 page.on('pageerror',e=>{state.page_errors.push(e.message);save()});
 page.on('console',m=>{if(m.type()==='error'&&!m.text().includes('favicon')){state.console_errors.push(m.text().slice(0,400));save()}});
 await page.route('https://box.nju.edu.cn/**',route=>route.abort());
 await page.goto(url+'/',{waitUntil:'domcontentloaded'});
 await page.getByRole('button',{name:'开始',exact:true}).click();
 await page.getByLabel('论文文件',{exact:true}).setInputFiles(pdf);
 note('ready_to_submit',{pdf_bytes:fs.statSync(pdf).size});
 await page.getByRole('button',{name:'开始查新'}).click();
 note('submit_clicked_once');
 try{await page.waitForURL(/\?run=[^&]+/,{timeout:45000})}catch(e){note('submission_response_unknown',{error:String(e).slice(0,200)});await page.screenshot({path:path.join(out,'submission-unknown.png')});save();await browser.close();return}
 const current=new URL(page.url());const id=current.searchParams.get('run');state.run_id=id;save();
 if(!id||state.posts.length!==1)throw new Error('business run identity or POST count mismatch');
 note('run_id_observed',{run_id:id});
 await page.screenshot({path:path.join(out,'after-submit.png')});
 const deadline=Date.now()+27*60*1000;let refreshed=false;let last='';let final=null;
 while(Date.now()<deadline){
  const response=await page.request.get(url+'/api/novelty/runs/'+encodeURIComponent(id),{timeout:20000}).catch(e=>null);
  if(response&&response.ok()){
   const snapshot=await response.json();
   if(snapshot.task_id!==id)throw new Error('task identity changed');
   const key=JSON.stringify([snapshot.status,snapshot.progress?.stage,snapshot.progress?.round,snapshot.updated_at,snapshot.error]);
   if(key!==last){last=key;state.snapshots.push({at:new Date().toISOString(),status:snapshot.status,stage:snapshot.progress?.stage??null,round:snapshot.progress?.round??null,updated_at:snapshot.updated_at,error:snapshot.error??null});save();note('snapshot',{status:snapshot.status,stage:snapshot.progress?.stage??null,round:snapshot.progress?.round??null})}
   if(!refreshed&&snapshot.status==='running'){
    await page.reload({waitUntil:'domcontentloaded'});refreshed=true;state.refresh_count=1;save();
    if(new URL(page.url()).searchParams.get('run')!==id||state.posts.length!==1)throw new Error('refresh created a second run');
    note('refreshed_same_run');
   }
   if(snapshot.status==='succeeded'||snapshot.status==='failed'){final=snapshot;break}
  }else{note('poll_network_issue',{http_status:response?.status()??null})}
  await new Promise(resolve=>setTimeout(resolve,10000));
 }
 state.finished_at=new Date().toISOString();state.final_status=final?.status??'deadline_without_terminal_snapshot';save();
 if(final?.status==='succeeded'){
  await page.goto(url+'/?run='+encodeURIComponent(id),{waitUntil:'domcontentloaded'});
  await page.getByRole('button',{name:'查看查新报告'}).click();
  await page.getByRole('button',{name:'下载',exact:true}).waitFor({timeout:30000});
  await page.screenshot({path:path.join(out,'final-report.png'),fullPage:true});
  const reportUrl=new URL(final.report.preview_url,url).href;
  const reportResponse=await page.request.get(reportUrl);const body=await reportResponse.body();
  const previewHash=crypto.createHash('sha256').update(body).digest('hex');
  const downloadPromise=page.waitForEvent('download');await page.getByRole('button',{name:'下载',exact:true}).click();
  const download=await downloadPromise;const downloadBytes=fs.readFileSync(await download.path());
  const downloadHash=crypto.createHash('sha256').update(downloadBytes).digest('hex');
  state.report={preview_http_status:reportResponse.status(),preview_sha256:previewHash,download_sha256:downloadHash,download_name:download.suggestedFilename(),bytes:body.length};save();
  note('report_checked',{preview_sha256:previewHash,download_sha256:downloadHash});
 }else{
  await page.screenshot({path:path.join(out,'final-or-stopped.png'),fullPage:true});
  note('run_stopped',{status:state.final_status});
 }
 await browser.close();
})().catch(e=>{state.fatal_observer_error=String(e);save();note('observer_error',{error:String(e).slice(0,400)});process.exitCode=1});
