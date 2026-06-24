"""Render the self-contained Gateshead Business Map dashboard from dashboard_data.json."""
import config as C

TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Gateshead Business Map &mdash; Companies House, IMD 2025 &amp; sector intelligence</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="">
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css">
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
<script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
<style>
:root{
  --bg:#f5f3ee;--surface:#fff;--surface-2:#fbfaf6;--ink:#1a1d24;--ink-2:#3a4150;--muted:#6b7280;
  --line:#e3dfd4;--line-2:#ebe7dc;--accent:#134e4a;--accent-2:#2a8d83;--accent-3:#d97706;
  --good:#15803d;--bad:#b91c1c;--warn:#b45309;--chip-bg:#ecede4;
  --shadow:0 1px 0 rgba(20,30,50,.04),0 1px 3px rgba(20,30,50,.06);--radius:10px;
}
*{box-sizing:border-box;}html,body{margin:0;padding:0;}
body{font-family:'Inter',system-ui,'Segoe UI',Roboto,Arial,sans-serif;background:var(--bg);color:var(--ink);font-size:15px;line-height:1.55;-webkit-font-smoothing:antialiased;}
.wrap{max-width:1240px;margin:0 auto;padding:8px 28px 80px;}
header.hero{background:linear-gradient(180deg,#fbfaf6 0%,#f5f3ee 100%);border-bottom:1px solid var(--line);}
.hero-inner{max-width:1240px;margin:0 auto;padding:22px 28px 16px;}
.eyebrow{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);font-weight:600;}
h1{font-family:'Source Serif 4',Georgia,serif;font-weight:600;font-size:36px;line-height:1.15;margin:6px 0 8px;letter-spacing:-.01em;}
.subtitle{color:var(--ink-2);max-width:820px;font-size:16px;}
.source{font-size:12px;color:var(--muted);margin-top:12px;}
.source code{background:var(--chip-bg);padding:1px 6px;border-radius:4px;font-size:11px;}
.hero-stats{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin-top:14px;}
.stat{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:13px 15px;box-shadow:var(--shadow);}
.stat .label{font-size:10.5px;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);font-weight:600;}
.stat .value{font-family:'Source Serif 4',Georgia,serif;font-weight:600;font-size:25px;line-height:1;margin:7px 0 3px;}
.stat .sub{font-size:11.5px;color:var(--ink-2);}
nav.tabs{position:sticky;top:0;z-index:600;background:rgba(245,243,238,.94);backdrop-filter:blur(8px);border-bottom:1px solid var(--line);}
.tabs-inner{max-width:1240px;margin:0 auto;padding:10px 28px;display:flex;gap:4px;flex-wrap:wrap;}
.tabs a{font-size:13px;font-weight:500;color:var(--ink-2);text-decoration:none;padding:7px 12px;border-radius:999px;border:1px solid transparent;}
.tabs a:hover{background:var(--surface);border-color:var(--line);}
.tabs a.active{background:var(--accent);color:#fff;}
section{margin-top:40px;scroll-margin-top:58px;}
section h2{font-family:'Source Serif 4',Georgia,serif;font-size:25px;font-weight:600;margin:0 0 6px;}
section .lede{color:var(--ink-2);margin-bottom:16px;max-width:900px;}
.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);padding:18px 20px;margin-bottom:18px;}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:18px;}
.grid2>.card{margin-bottom:0;}
#map{height:calc(100vh - 230px);min-height:540px;border-radius:var(--radius);border:1px solid var(--line);box-shadow:var(--shadow);}
.leaflet-top.leaflet-right .ctl{background:#fff;border:1px solid var(--line);border-radius:8px;box-shadow:var(--shadow);padding:10px 12px;font-size:12.5px;max-width:225px;max-height:560px;overflow:auto;}
.ctl-h{font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:.05em;font-size:10.5px;margin:9px 0 4px;}
.ctl-h:first-child{margin-top:0;}
.ctl label{display:flex;align-items:center;gap:6px;margin:2px 0;cursor:pointer;line-height:1.3;}
.ctl select{width:100%;margin:2px 0;font-size:12px;padding:3px;border:1px solid var(--line);border-radius:5px;}
.legend{background:#fff;border:1px solid var(--line);border-radius:8px;box-shadow:var(--shadow);padding:9px 11px;font-size:12px;line-height:1.5;}
.legend i{width:14px;height:14px;display:inline-block;margin-right:6px;border-radius:3px;vertical-align:-2px;opacity:.85;}
.legend .lt{font-weight:700;font-size:10.5px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);margin-bottom:4px;}
table{border-collapse:collapse;width:100%;font-size:13px;}
th,td{text-align:left;padding:6px 9px;border-bottom:1px solid var(--line-2);}
th{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);font-weight:600;cursor:default;}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;}
.bar{height:7px;border-radius:4px;background:var(--accent);display:inline-block;vertical-align:middle;}
.chip{display:inline-block;font-size:10.5px;font-weight:600;padding:1px 7px;border-radius:999px;background:var(--chip-bg);color:var(--ink-2);}
.note{font-size:12.5px;color:var(--muted);margin-top:8px;}
.warnbox{background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;padding:10px 13px;font-size:12.5px;color:#7c2d12;}
.kbox{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:8px;}
.kbox .k{background:var(--surface-2);border:1px solid var(--line-2);border-radius:8px;padding:8px 10px;font-size:12px;}
.kbox .k b{display:block;font-size:18px;font-family:'Source Serif 4',serif;}
a.src{color:var(--accent);text-decoration:none;}a.src:hover{text-decoration:underline;}
footer{margin-top:40px;padding-top:18px;border-top:1px solid var(--line);font-size:12px;color:var(--muted);}
.chartwrap{position:relative;height:380px;}
@media(max-width:980px){.hero-stats{grid-template-columns:repeat(3,1fr);}.grid2{grid-template-columns:1fr;}}
@media(max-width:640px){.wrap,.hero-inner,.tabs-inner{padding-left:14px;padding-right:14px;}h1{font-size:24px;}.hero-stats{grid-template-columns:repeat(2,1fr);}}
</style>
</head>
<body>
<header class="hero"><div class="hero-inner">
  <div class="eyebrow">Economic Intelligence &middot; Business, industry &amp; trade</div>
  <h1>Gateshead Business Map</h1>
  <div class="subtitle">Every company registered in Gateshead borough, mapped and enriched with deprivation, sector churn, food premises and innovation data &mdash; built to find areas for <b>intervention</b> (where the local economy needs support) and <b>investment</b> (where it could land well).</div>
  <div class="source" id="sourceLine"></div>
  <div class="hero-stats" id="heroStats"></div>
</div></header>

<nav class="tabs"><div class="tabs-inner">
  <a href="#mapview" class="active">Map</a>
  <a href="#overview">Overview</a>
  <a href="#sectors">Sectors &amp; saturation</a>
  <a href="#scores">Intervention &amp; investment</a>
  <a href="#innovation">Innovation</a>
  <a href="#about">About &amp; caveats</a>
</div></nav>

<div class="wrap">

<section id="mapview">
  <h2>Street-level business map</h2>
  <div class="lede">Every company registered in Gateshead at its <b>postcode location</b> &mdash; zoom in to street level to see individual firms. FSA food premises are shown at their exact location. Switch the area shading, filter by sector or status, and hide mass-registration addresses where many unrelated firms share one registered office.</div>
  <div id="map"></div>
  <div class="note" id="mapNote"></div>
</section>

<section id="overview">
  <h2>Overview</h2>
  <div class="lede" id="overviewLede"></div>
  <div class="grid2">
    <div class="card"><h3 style="margin:0 0 10px;font-size:15px;">Business base at a glance</h3><div class="kbox" id="kbox"></div></div>
    <div class="card"><h3 style="margin:0 0 10px;font-size:15px;">Top sectors by registered companies</h3><div class="chartwrap" style="height:300px;"><canvas id="sectorChart"></canvas></div></div>
  </div>
  <div class="card"><h3 style="margin:0 0 4px;font-size:15px;">What the scores say</h3>
    <div class="note" style="margin-bottom:10px;">Population-weighted ward roll-ups. Higher intervention = greater need for support; higher investment = stronger opportunity signal. Both 0&ndash;100, relative within Gateshead.</div>
    <div class="grid2"><div id="topInter"></div><div id="topInvest"></div></div>
  </div>
</section>

<section id="sectors">
  <h2>Sectors &amp; saturation</h2>
  <div class="lede">The saturation lens: how many businesses each industry supports per 1,000 residents (supply) against that industry's <b>death rate</b> from ONS Business Demography 2024 (churn). Upper-right = over-supplied <i>and</i> high-churn &mdash; the classic "too many that keep failing" pattern (e.g. accommodation &amp; food). Lower-right = well-supplied and stable; left = thinner provision.</div>
  <div class="grid2">
    <div class="card"><div class="chartwrap"><canvas id="satChart"></canvas></div></div>
    <div class="card"><h3 style="margin:0 0 8px;font-size:15px;">Sectors by SIC section</h3><div style="max-height:360px;overflow:auto;"><table id="sectorTable"></table></div></div>
  </div>
</section>

<section id="scores">
  <h2>Intervention &amp; investment</h2>
  <div class="lede">Composite indices built from real signals, each normalised across Gateshead's 126 LSOAs and re-normalised when a signal is unavailable. Weights are shown in <a href="#about" class="src">About</a> and are editable in the build config.</div>
  <div class="grid2">
    <div class="card"><h3 style="margin:0 0 8px;font-size:15px;color:var(--bad);">Highest intervention need (wards)</h3><table id="interTable"></table></div>
    <div class="card"><h3 style="margin:0 0 8px;font-size:15px;color:var(--good);">Strongest investment signal (wards)</h3><table id="investTable"></table></div>
  </div>
  <div class="card"><h3 style="margin:0 0 8px;font-size:15px;">Signal composition</h3>
    <div class="note">Intervention = deprivation (IMD 2025), live business distress (CH liquidation/administration), sector fragility (local mix &times; ONS death rates). Investment = growth sectors, dynamism (recent incorporations), agglomeration (business density), underserved demand (residents per consumer premise). Vacancy and per-LSOA innovation are not yet wired &mdash; see caveats.</div>
  </div>
</section>

<section id="innovation">
  <h2>Innovation</h2>
  <div class="lede">Publicly-funded research &amp; innovation projects associated with Gateshead, from UKRI's Gateway to Research (includes Innovate UK). Borough-level &mdash; not yet geocoded to LSOA, so it informs context rather than the per-area score.</div>
  <div class="grid2">
    <div class="card"><h3 style="margin:0 0 8px;font-size:15px;">Projects by funder</h3><div class="chartwrap" style="height:300px;"><canvas id="funderChart"></canvas></div></div>
    <div class="card"><h3 style="margin:0 0 8px;font-size:15px;">Funded projects</h3><div style="max-height:330px;overflow:auto;"><table id="innovTable"></table></div></div>
  </div>
</section>

<section id="about">
  <h2>About &amp; caveats</h2>
  <div class="card">
    <h3 style="margin:0 0 8px;font-size:15px;">Data sources (all free &amp; keyless)</h3>
    <ul style="margin:0 0 6px 18px;font-size:13.5px;line-height:1.7;">
      <li><b>Companies House</b> &mdash; Free Company Data Product (live companies; registered office, SIC, status, incorporation).</li>
      <li><b>postcodes.io</b> &mdash; geocoding postcode &rarr; lat/long, LSOA 2021, ward, local authority.</li>
      <li><b>IMD 2025 (IoD2025, MHCLG)</b> &mdash; deprivation by LSOA 2021 (File 7: ranks, deciles, scores, population).</li>
      <li><b>ONS Business Demography 2024</b> &mdash; birth &amp; death rates by industry (sector churn signal).</li>
      <li><b>Nomis (BRES)</b> &mdash; employees supported.</li>
      <li><b>Food Standards Agency</b> &mdash; food premises &amp; hygiene ratings (real trading locations).</li>
      <li><b>UKRI Gateway to Research</b> &mdash; innovation/R&amp;D projects.</li>
      <li><b>ONS Open Geography Portal</b> &mdash; LSOA 2021 + Ward 2024 boundaries and lookup.</li>
    </ul>
  </div>
  <div class="grid2">
    <div class="card"><h3 style="margin:0 0 8px;font-size:15px;">Caveats &mdash; read these</h3>
      <ul style="margin:0 0 0 18px;font-size:13px;line-height:1.65;">
        <li><b>Registered office &ne; trading address.</b> Companies House locates where a firm is <i>registered</i>, often an accountant or home. Mass-registration addresses are flagged and can be hidden on the map. FSA premises are the ground-truth trading locations.</li>
        <li><b>Sector churn is national by industry.</b> ONS publishes birth/death rates by broad industry, applied to Gateshead's local sector mix &mdash; not street-level survival.</li>
        <li><b>Employees</b> are a borough total (BRES), not per-area.</li>
        <li><b>Closures</b> use ONS death rates, not enumerated dissolutions (the free CH product is live-only).</li>
        <li><b>Vacancy</b> (council NNDR) and <b>per-LSOA innovation</b> are not yet wired; those score signals are omitted and weights re-normalised.</li>
      </ul>
    </div>
    <div class="card"><h3 style="margin:0 0 8px;font-size:15px;">Scoring weights &amp; build notes</h3>
      <div id="weightsBox" style="font-size:12.5px;"></div>
      <div id="warnBox" style="margin-top:10px;"></div>
    </div>
  </div>
</section>

<footer id="footer"></footer>
</div>

<script>window.DATA = __DATA__;</script>
<script>
(function(){
const D = window.DATA, H = D.headline, M = D.meta;
const SEC_COLORS={A:'#8c6d31',B:'#7b4173',C:'#3182bd',D:'#e6550d',E:'#2ca25f',F:'#fd8d3c',G:'#e7298a',H:'#1f78b4',I:'#d62728',J:'#6a3d9a',K:'#b15928',L:'#17becf',M:'#2c7fb8',N:'#756bb1',O:'#969696',P:'#66a61e',Q:'#1b9e77',R:'#e6ab02',S:'#a6761d',T:'#777',U:'#777',X:'#bbb'};
const SECL = D.section_labels;
const fmt = n => (n==null?'&ndash;':Number(n).toLocaleString());
const esc = s => (s==null?'':String(s)).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const secLabel = s => SECL[s]||s;

// ---------- header ----------
document.getElementById('sourceLine').innerHTML =
  'Companies House snapshot <code>'+esc(M.ch_snapshot)+'</code> &middot; '+esc(M.imd_vintage)+' &middot; wards '+esc(M.ward_vintage)+' &middot; built '+esc(M.generated);
const hs=[['Companies',fmt(H.companies),'registered in borough'],['Active',fmt(H.active),(100*H.active/H.companies).toFixed(0)+'% of total'],
  ['In distress',fmt(H.distress),'liquidation / administration'],['Food premises',fmt(H.fsa),'FSA-rated'],
  ['Employees',fmt(H.employees),'BRES (borough)'],['Residents',fmt(H.population),H.lsoas+' LSOAs / '+H.wards+' wards']];
document.getElementById('heroStats').innerHTML = hs.map(s=>'<div class="stat"><div class="label">'+s[0]+'</div><div class="value">'+s[1]+'</div><div class="sub">'+s[2]+'</div></div>').join('');

// ---------- overview ----------
const wards = Object.keys(D.ward_scores).map(cd=>Object.assign({cd:cd,name:D.ward_names[cd]||cd},D.ward_scores[cd]));
const topI = wards.filter(w=>w.intervention!=null).slice().sort((a,b)=>b.intervention-a.intervention);
const topV = wards.filter(w=>w.investment!=null).slice().sort((a,b)=>b.investment-a.investment);
const secI = D.sectors.find(s=>s.sec==='I')||{};
document.getElementById('overviewLede').innerHTML =
  'Gateshead has <b>'+fmt(H.companies)+'</b> registered companies supporting around <b>'+fmt(H.employees)+'</b> jobs across <b>'+H.wards+'</b> wards. '+
  'The UK 2024 business death rate is '+H.uk.death_rate+'% and five-year survival '+H.uk.survival_5yr+'%. '+
  'Highest intervention need centres on <b>'+esc(topI[0].name)+'</b>; the strongest investment signal is in <b>'+esc(topV[0].name)+'</b>. '+
  (secI.count? 'Accommodation &amp; food runs '+fmt(secI.count)+' firms ('+secI.per_1k+' per 1,000 residents) against a '+secI.death+'% industry death rate &mdash; the over-supply-and-churn pattern.':'');
document.getElementById('kbox').innerHTML = [
  ['Companies',fmt(H.companies)],['Active',fmt(H.active)],['In distress',fmt(H.distress)],
  ['Food premises',fmt(H.fsa)],['Jobs (BRES)',fmt(H.employees)],['Residents',fmt(H.population)],
  ['LSOAs',fmt(H.lsoas)],['Wards',fmt(H.wards)]].map(k=>'<div class="k"><b>'+k[1]+'</b>'+k[0]+'</div>').join('');
function wardMini(list,key,color){
  const max=Math.max.apply(null,list.map(w=>w[key]));
  return '<table><tr><th>Ward</th><th class="num">Score</th><th></th></tr>'+list.slice(0,6).map(w=>
    '<tr><td>'+esc(w.name)+'</td><td class="num">'+w[key].toFixed(1)+'</td><td style="width:45%"><span class="bar" style="width:'+(100*w[key]/max)+'%;background:'+color+'"></span></td></tr>').join('')+'</table>';
}
document.getElementById('topInter').innerHTML='<h4 style="margin:0 0 4px;color:var(--bad);font-size:13px;">Intervention</h4>'+wardMini(topI,'intervention','#de2d26');
document.getElementById('topInvest').innerHTML='<h4 style="margin:0 0 4px;color:var(--good);font-size:13px;">Investment</h4>'+wardMini(topV,'investment','#31a354');

// ---------- map ----------
const map = L.map('map',{scrollWheelZoom:false}).setView([54.93,-1.66],12);
map.on('focus',()=>map.scrollWheelZoom.enable()); map.on('blur',()=>map.scrollWheelZoom.disable());
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',{
  attribution:'&copy; OpenStreetMap &copy; CARTO',subdomains:'abcd',maxZoom:19}).addTo(map);

const RAMPS={intervention:['#fee5d9','#fcae91','#fb6a4a','#de2d26','#a50f15'],
  investment:['#edf8e9','#bae4b3','#74c476','#31a354','#006d2c'],
  density:['#eff3ff','#bdd7e7','#6baed6','#3182bd','#08519c']};
const IMD=['#a50026','#d73027','#f46d43','#fdae61','#fee08b','#d9ef8b','#a6d96a','#66bd63','#1a9850','#006837'];
function metricVal(cd,m){const s=D.lsoa_scores[cd];if(!s)return null;
  if(m==='imd')return s.imd_decile;if(m==='density')return s.density;return s[m];}
const breaks={};
['intervention','investment','density'].forEach(m=>{
  const vs=Object.values(D.lsoa_scores).map(s=>m==='density'?s.density:s[m]).filter(v=>v!=null);
  const lo=Math.min.apply(null,vs),hi=Math.max.apply(null,vs);
  breaks[m]=[0,1,2,3,4].map(i=>lo+(hi-lo)*i/5);
});
function colorFor(m,v){if(v==null)return '#d9d4c8';
  if(m==='imd'){const i=Math.min(10,Math.max(1,Math.round(v)));return IMD[i-1];}
  const b=breaks[m],r=RAMPS[m];for(let i=b.length-1;i>=0;i--){if(v>=b[i])return r[i];}return r[0];}
let metric='intervention';
function styleLsoa(f){const v=metricVal(f.properties.LSOA21CD,metric);
  return {fillColor:colorFor(metric,v),weight:.6,color:'#fff',fillOpacity:v==null?.15:.72};}
const lsoaLayer=L.geoJSON(D.boundaries.lsoa,{style:styleLsoa,onEachFeature:(f,l)=>{
  const cd=f.properties.LSOA21CD,s=D.lsoa_scores[cd]||{};
  l.bindPopup('<b>LSOA '+cd+'</b><br>Intervention <b>'+(s.intervention!=null?s.intervention.toFixed(1):'&ndash;')+'</b> &middot; Investment <b>'+(s.investment!=null?s.investment.toFixed(1):'&ndash;')+'</b>'+
    '<br>IMD 2025 decile: '+(s.imd_decile||'&ndash;')+' (1=most deprived)<br>Companies: '+fmt(s.n)+' &middot; recent: '+fmt(s.recent)+' &middot; distress: '+fmt(s.distress)+'<br>Residents: '+fmt(s.pop)+' &middot; density: '+(s.density||'&ndash;')+'/1k');
}}).addTo(map);
map.fitBounds(lsoaLayer.getBounds(),{padding:[10,10]});

const wardLayer=L.geoJSON(D.boundaries.ward,{style:{fill:false,color:'#134e4a',weight:1.6,opacity:.7,dashArray:'4 3'},
  onEachFeature:(f,l)=>{const cd=f.properties.WD24CD,s=D.ward_scores[cd]||{};
    l.bindPopup('<b>'+esc(f.properties.WD24NM)+'</b><br>Intervention <b>'+(s.intervention!=null?s.intervention.toFixed(1):'&ndash;')+'</b> &middot; Investment <b>'+(s.investment!=null?s.investment.toFixed(1):'&ndash;')+'</b><br>Companies: '+fmt(s.n)+' &middot; residents: '+fmt(s.pop));}});

// companies (clustered)
const compLayer=L.markerClusterGroup({chunkedLoading:true,maxClusterRadius:50,disableClusteringAtZoom:15,spiderfyOnMaxZoom:true});
function rebuildCompanies(){
  compLayer.clearLayers();
  const sec=document.getElementById('fSec').value,st=document.getElementById('fStatus').value,hide=document.getElementById('fHideCl').checked;
  const arr=[];
  for(const c of D.companies){
    if(sec!=='all'&&c.sec!==sec)continue;
    if(st==='active'&&c.st.toLowerCase().indexOf('active')<0)continue;
    if(st==='distress'&&!c.ds)continue;
    if(hide&&c.cl)continue;
    const m=L.circleMarker([c.lat,c.lon],{radius:4,weight:.5,color:'#fff',fillColor:SEC_COLORS[c.sec]||'#888',fillOpacity:.85});
    m.bindPopup('<b>'+esc(c.n)+'</b><br>'+esc(secLabel(c.sec))+' &middot; SIC '+esc(c.sic)+'<br>'+esc(c.desc)+'<br>Status: '+esc(c.st)+(c.iy?' &middot; inc '+c.iy:'')+(c.cl?'<br><i>mass-registration address</i>':''));
    arr.push(m);
  }
  compLayer.addLayers(arr);
  document.getElementById('mapNote').innerHTML='Showing <b>'+fmt(arr.length)+'</b> companies'+(sec!=='all'?' in '+esc(secLabel(sec)):'')+(st!=='all'?' ('+st+')':'')+(hide?', mass-registration hidden':'')+'.';
}
const fsaLayer=L.layerGroup();
function ratingColor(r){if(r==='5')return '#1a9850';if(r==='4')return '#66bd63';if(r==='3')return '#fee08b';if(r==='2'||r==='1'||r==='0')return '#d73027';return '#999';}
for(const f of D.fsa){const m=L.circleMarker([f.lat,f.lon],{radius:3,weight:0,fillColor:ratingColor(f.rt),fillOpacity:.85});
  m.bindPopup('<b>'+esc(f.n)+'</b><br>'+esc(f.ty)+'<br>Hygiene rating: <b>'+esc(f.rt)+'</b>');fsaLayer.addLayer(m);}
compLayer.addTo(map);

// custom control
const ctl=L.control({position:'topright'});
ctl.onAdd=function(){
  const d=L.DomUtil.create('div','ctl');
  const opts=D.sectors.map(s=>'<option value="'+s.sec+'">'+esc(secLabel(s.sec))+' ('+s.count+')</option>').join('');
  d.innerHTML=
   '<div class="ctl-h">Area shading</div>'+
   '<label><input type="radio" name="m" value="intervention" checked> Intervention score</label>'+
   '<label><input type="radio" name="m" value="investment"> Investment score</label>'+
   '<label><input type="radio" name="m" value="imd"> IMD 2025 decile</label>'+
   '<label><input type="radio" name="m" value="density"> Business density</label>'+
   '<div class="ctl-h">Layers</div>'+
   '<label><input type="checkbox" id="ckBiz" checked> Businesses</label>'+
   '<label><input type="checkbox" id="ckFsa"> Food premises</label>'+
   '<label><input type="checkbox" id="ckWard"> Ward boundaries</label>'+
   '<label><input type="checkbox" id="ckLsoa" checked> Area shading</label>'+
   '<div class="ctl-h">Business filters</div>'+
   '<select id="fSec"><option value="all">All sectors</option>'+opts+'</select>'+
   '<select id="fStatus"><option value="all">All statuses</option><option value="active">Active only</option><option value="distress">In distress</option></select>'+
   '<label><input type="checkbox" id="fHideCl"> Hide mass-registration</label>';
  L.DomEvent.disableClickPropagation(d);L.DomEvent.disableScrollPropagation(d);
  return d;
};
ctl.addTo(map);

// legend
const legend=L.control({position:'bottomright'});
legend.onAdd=function(){this._div=L.DomUtil.create('div','legend');this.update();return this._div;};
legend.update=function(){
  let html='<div class="lt">'+({intervention:'Intervention score',investment:'Investment score',imd:'IMD 2025 decile',density:'Businesses / 1k residents'}[metric])+'</div>';
  if(metric==='imd'){html+='<div><i style="background:'+IMD[0]+'"></i>1 most deprived</div><div><i style="background:'+IMD[4]+'"></i>5</div><div><i style="background:'+IMD[9]+'"></i>10 least deprived</div>';}
  else{const b=breaks[metric],r=RAMPS[metric];for(let i=0;i<r.length;i++){html+='<div><i style="background:'+r[i]+'"></i>'+Math.round(b[i])+'+'+'</div>';}}
  this._div.innerHTML=html;};
legend.addTo(map);

// control wiring (after DOM exists)
document.querySelectorAll('input[name=m]').forEach(r=>r.addEventListener('change',e=>{
  metric=e.target.value;lsoaLayer.setStyle(styleLsoa);legend.update();}));
document.getElementById('ckBiz').addEventListener('change',e=>{e.target.checked?compLayer.addTo(map):map.removeLayer(compLayer);});
document.getElementById('ckFsa').addEventListener('change',e=>{e.target.checked?fsaLayer.addTo(map):map.removeLayer(fsaLayer);});
document.getElementById('ckWard').addEventListener('change',e=>{e.target.checked?wardLayer.addTo(map):map.removeLayer(wardLayer);});
document.getElementById('ckLsoa').addEventListener('change',e=>{e.target.checked?lsoaLayer.addTo(map):map.removeLayer(lsoaLayer);});
['fSec','fStatus','fHideCl'].forEach(id=>document.getElementById(id).addEventListener('change',rebuildCompanies));
// map-first: the container is sized after init, so fix the size, refit, THEN cluster
function initMapContent(){ map.invalidateSize(); map.fitBounds(lsoaLayer.getBounds(),{padding:[10,10]}); rebuildCompanies(); }
if(document.readyState==='complete'){ setTimeout(initMapContent,60); } else { window.addEventListener('load',function(){ setTimeout(initMapContent,60); }); }
window.GBM={map:map,companies:compLayer,fsa:fsaLayer,rebuild:rebuildCompanies};   // handle for debugging / power users

// ---------- charts ----------
const topSecs=D.sectors.slice(0,12);
new Chart(document.getElementById('sectorChart'),{type:'bar',
  data:{labels:topSecs.map(s=>secLabel(s.sec)),datasets:[{data:topSecs.map(s=>s.count),backgroundColor:topSecs.map(s=>SEC_COLORS[s.sec]||'#888')}]},
  options:{indexAxis:'y',plugins:{legend:{display:false}},scales:{x:{title:{display:true,text:'Registered companies'}}}}});

const sat=D.sectors.filter(s=>s.per_1k!=null&&s.count>=20).map(s=>({x:s.per_1k,y:s.death,r:Math.max(5,Math.sqrt(s.count)*0.85),sec:s.sec,label:secLabel(s.sec),count:s.count,birth:s.birth}));
const medX=sat.map(d=>d.x).sort((a,b)=>a-b)[Math.floor(sat.length/2)];
const refY=H.uk.death_rate;
const quad={id:'quad',afterDraw(ch){const a=ch.chartArea,x=ch.scales.x,y=ch.scales.y,ctx=ch.ctx;const px=x.getPixelForValue(medX),py=y.getPixelForValue(refY);
  ctx.save();ctx.strokeStyle='#bbb';ctx.setLineDash([4,4]);
  ctx.beginPath();ctx.moveTo(px,a.top);ctx.lineTo(px,a.bottom);ctx.moveTo(a.left,py);ctx.lineTo(a.right,py);ctx.stroke();
  ctx.setLineDash([]);ctx.fillStyle='#9a3412';ctx.font='600 10px Inter';ctx.textAlign='right';
  ctx.fillText('over-supplied + high churn',a.right-6,a.top+13);ctx.restore();}};
const letters={id:'let',afterDatasetsDraw(ch){const ctx=ch.ctx;ch.getDatasetMeta(0).data.forEach((pt,i)=>{
  ctx.save();ctx.fillStyle='#fff';ctx.font='700 10px Inter';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(sat[i].sec,pt.x,pt.y);ctx.restore();});}};
new Chart(document.getElementById('satChart'),{type:'bubble',
  data:{datasets:[{data:sat,backgroundColor:sat.map(d=>SEC_COLORS[d.sec]+'cc'),borderColor:'#fff',borderWidth:1}]},
  options:{plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>{const d=c.raw;return [d.label,d.count+' firms · '+d.x+' per 1k residents','death '+d.y+'% · birth '+d.birth+'%'];}}}},
    scales:{x:{title:{display:true,text:'Businesses per 1,000 residents (supply)'}},y:{title:{display:true,text:'Industry death rate % — ONS 2024 (churn)'}}}},
  plugins:[quad,letters]});

const fund={};D.innovation.projects.forEach(p=>{const f=p.funder||'Other';fund[f]=(fund[f]||0)+1;});
const fk=Object.keys(fund).sort((a,b)=>fund[b]-fund[a]);
new Chart(document.getElementById('funderChart'),{type:'doughnut',
  data:{labels:fk,datasets:[{data:fk.map(k=>fund[k]),backgroundColor:['#134e4a','#2a8d83','#d97706','#6a3d9a','#b15928','#1f78b4','#999','#e7298a']}]},
  options:{plugins:{legend:{position:'right',labels:{boxWidth:12,font:{size:11}}}}}});

// ---------- tables ----------
document.getElementById('sectorTable').innerHTML='<tr><th>Sec</th><th>Industry</th><th class="num">Firms</th><th class="num">/1k</th><th class="num">Birth%</th><th class="num">Death%</th></tr>'+
  D.sectors.map(s=>'<tr><td><span class="chip" style="background:'+(SEC_COLORS[s.sec]||'#ccc')+'33;color:'+(SEC_COLORS[s.sec]||'#555')+'">'+s.sec+'</span></td><td>'+esc(secLabel(s.sec))+'</td><td class="num">'+fmt(s.count)+'</td><td class="num">'+(s.per_1k||'')+'</td><td class="num">'+s.birth+'</td><td class="num">'+s.death+'</td></tr>').join('');
function scoreTable(list,key){return '<tr><th>Ward</th><th class="num">Score</th><th class="num">Firms</th><th class="num">Distress</th><th class="num">Pop</th></tr>'+
  list.slice(0,12).map(w=>'<tr><td>'+esc(w.name)+'</td><td class="num"><b>'+w[key].toFixed(1)+'</b></td><td class="num">'+fmt(w.n)+'</td><td class="num">'+fmt(w.distress)+'</td><td class="num">'+fmt(w.pop)+'</td></tr>').join('');}
document.getElementById('interTable').innerHTML=scoreTable(topI,'intervention');
document.getElementById('investTable').innerHTML=scoreTable(topV,'investment');
document.getElementById('innovTable').innerHTML='<tr><th>Project</th><th>Funder</th><th>Status</th></tr>'+
  D.innovation.projects.map(p=>'<tr><td>'+esc(p.title)+'</td><td>'+esc(p.funder)+'</td><td><span class="chip">'+esc(p.status)+'</span></td></tr>').join('');

// ---------- about ----------
function wTable(o){return '<table>'+Object.keys(o).map(k=>'<tr><td>'+k.replace(/_/g,' ')+'</td><td class="num">'+(o[k]*100).toFixed(0)+'%</td></tr>').join('')+'</table>';}
document.getElementById('weightsBox').innerHTML='<b>Intervention</b>'+wTable(M.weights.intervention)+'<b style="display:block;margin-top:6px;">Investment</b>'+wTable(M.weights.investment);
document.getElementById('warnBox').innerHTML='<div class="warnbox"><b>Build notes:</b><ul style="margin:4px 0 0 16px;padding:0;">'+(M.warnings.length?M.warnings.map(w=>'<li>'+esc(w)+'</li>').join(''):'<li>none</li>')+'</ul></div>';
document.getElementById('footer').innerHTML='Part of the <a class="src" href="../index.html">Economic Intelligence</a> dashboard collection &middot; data &copy; Crown copyright / open licences &middot; generated '+esc(M.generated)+' &middot; map tiles &copy; OpenStreetMap, CARTO.';

// ---------- tab highlighting ----------
const links=[].slice.call(document.querySelectorAll('nav.tabs a'));
const secs=links.map(a=>document.querySelector(a.getAttribute('href')));
window.addEventListener('scroll',()=>{let i=secs.length-1;for(;i>0;i--){if(secs[i].getBoundingClientRect().top<120)break;}
  links.forEach(l=>l.classList.remove('active'));links[i].classList.add('active');});
})();
</script>
</body>
</html>
"""

def main():
    data_text = (C.CACHE_DIR / "dashboard_data.json").read_text(encoding="utf-8")
    data_text = data_text.replace("</", "<\\/")          # prevent </script> breakout
    html = TEMPLATE.replace("__DATA__", data_text)
    C.OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    C.OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"wrote {C.OUTPUT_HTML} ({C.OUTPUT_HTML.stat().st_size/1e6:,.1f} MB)")

if __name__ == "__main__":
    main()
