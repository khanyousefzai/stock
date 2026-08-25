REPORT_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,700&family=JetBrains+Mono:wght@400;500;700&display=swap">
<style>
:root{
  --ground:#F5F1E6; --ground-2:#EFEADB; --surface:#FDFBF5; --surface-2:#F1EDE0;
  --ink:#1C2320; --ink-2:#4E5A53; --ink-3:#828C85;
  --rule:#DED6C3; --rule-2:#CBC2AC;
  --jade:#1a6b57; --jade-2:#12503f; --jade-soft:#E1EBE5; --jade-line:#B8D2C6;
  --amber:#8E6412; --amber-soft:#F3E9D3;
  --clay:#9C3527; --clay-soft:#F6E1DC;
  --shadow:0 1px 2px rgba(28,35,32,.05), 0 8px 24px -14px rgba(28,35,32,.18);
  --star:#1a6b57;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#121614; --ground-2:#171C19; --surface:#1B211E; --surface-2:#232A26;
    --ink:#EAE5D7; --ink-2:#AEB8B1; --ink-3:#79837C;
    --rule:#2C3531; --rule-2:#3B4640;
    --jade:#59B694; --jade-2:#7FCDAE; --jade-soft:#172C24; --jade-line:#2A4A3D;
    --amber:#D8A64C; --amber-soft:#2B2416;
    --clay:#E0806B; --clay-soft:#33201B;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -14px rgba(0,0,0,.7);
    --star:#59B694;
  }
}
:root[data-theme="dark"]{
  --ground:#121614; --ground-2:#171C19; --surface:#1B211E; --surface-2:#232A26;
  --ink:#EAE5D7; --ink-2:#AEB8B1; --ink-3:#79837C;
  --rule:#2C3531; --rule-2:#3B4640;
  --jade:#59B694; --jade-2:#7FCDAE; --jade-soft:#172C24; --jade-line:#2A4A3D;
  --amber:#D8A64C; --amber-soft:#2B2416;
  --clay:#E0806B; --clay-soft:#33201B;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -14px rgba(0,0,0,.7);
  --star:#59B694;
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:"DM Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
  font-size:15px; line-height:1.62; -webkit-font-smoothing:antialiased;
}
.wrap{max-width:1180px; margin:0 auto; padding:0 22px 90px}
.num,.mono{font-family:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace; font-variant-numeric:tabular-nums}

/* ---------- header ---------- */
.hero{position:relative; overflow:hidden; background:var(--ground-2); border-bottom:1px solid var(--rule)}
#stars{position:absolute; inset:0; width:100%; height:100%; opacity:.16; pointer-events:none}
:root[data-theme="dark"] #stars{opacity:.22}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) #stars{opacity:.22}}
.hero-in{position:relative; max-width:1180px; margin:0 auto; padding:46px 22px 34px; display:flex;
         flex-wrap:wrap; gap:26px; align-items:flex-end; justify-content:space-between}
.brand{display:flex; flex-direction:column; gap:6px; min-width:min(100%,420px)}
.eyebrow{font-size:11px; letter-spacing:.20em; text-transform:uppercase; color:var(--jade); font-weight:500}
h1{font-family:"Cormorant Garamond",Georgia,serif; font-weight:600; font-size:clamp(40px,6.4vw,68px);
   line-height:.98; margin:0; letter-spacing:-.015em; text-wrap:balance}
.sub{color:var(--ink-2); font-size:14.5px; max-width:56ch; margin:4px 0 0}
.stamp{display:flex; flex-direction:column; gap:3px; align-items:flex-end; text-align:right}
.stamp .big{font-family:"JetBrains Mono",monospace; font-size:15px; font-weight:500; color:var(--ink)}
.stamp .sm{font-size:11.5px; color:var(--ink-3); letter-spacing:.04em}
.live{display:inline-flex; align-items:center; gap:7px; background:var(--jade-soft); color:var(--jade);
      border:1px solid var(--jade-line); border-radius:2px; padding:3px 9px; font-size:11px;
      letter-spacing:.13em; text-transform:uppercase; font-weight:500}
.live::before{content:""; width:6px; height:6px; border-radius:50%; background:var(--jade)}

/* ---------- nav ---------- */
nav{position:sticky; top:0; z-index:40; background:color-mix(in srgb, var(--ground) 88%, transparent);
    backdrop-filter:blur(10px); border-bottom:1px solid var(--rule)}
.nav-in{max-width:1180px; margin:0 auto; padding:0 22px; display:flex; gap:2px; overflow-x:auto}
nav a{flex:0 0 auto; padding:11px 12px; font-size:12.5px; color:var(--ink-2); text-decoration:none;
      border-bottom:2px solid transparent; white-space:nowrap}
nav a:hover{color:var(--jade); border-bottom-color:var(--jade-line)}
nav a:focus-visible{outline:2px solid var(--jade); outline-offset:-2px}
nav .k{font-family:"JetBrains Mono",monospace; color:var(--jade); margin-right:5px; font-size:11px}

/* ---------- sections ---------- */
section{margin-top:56px; scroll-margin-top:60px}
.sec-head{display:flex; align-items:baseline; gap:14px; border-bottom:1px solid var(--rule-2); padding-bottom:9px; margin-bottom:8px}
.sec-key{font-family:"JetBrains Mono",monospace; font-size:12px; color:var(--jade); font-weight:700; letter-spacing:.06em}
.sec-head h2{font-family:"Cormorant Garamond",Georgia,serif; font-weight:600; font-size:31px; margin:0; letter-spacing:-.01em}
.sec-note{color:var(--ink-3); font-size:12.5px; margin-left:auto; text-align:right}
.lede{color:var(--ink-2); font-size:14.5px; max-width:76ch; margin:12px 0 22px}

/* ---------- summary strip ---------- */
.strip{display:grid; grid-template-columns:repeat(auto-fit,minmax(128px,1fr)); gap:1px;
       background:var(--rule); border:1px solid var(--rule); margin-top:26px; border-radius:3px; overflow:hidden}
.sc{background:var(--surface); padding:14px 16px; display:flex; flex-direction:column; gap:2px}
.sc .l{font-size:10.5px; letter-spacing:.14em; text-transform:uppercase; color:var(--ink-3)}
.sc .v{font-family:"JetBrains Mono",monospace; font-size:24px; font-weight:500; line-height:1.15}
.sc .m{font-size:11.5px; color:var(--ink-3)}
.sc.hi .v{color:var(--jade)}

/* ---------- tables ---------- */
.tw{overflow-x:auto; border:1px solid var(--rule); border-radius:3px; background:var(--surface); box-shadow:var(--shadow)}
table{border-collapse:collapse; width:100%; min-width:820px; font-size:13.5px}
thead th{position:sticky; top:0; background:var(--surface-2); text-align:left; padding:10px 12px;
         font-size:10.5px; letter-spacing:.11em; text-transform:uppercase; color:var(--ink-2);
         font-weight:500; border-bottom:1px solid var(--rule-2); white-space:nowrap}
tbody td{padding:9px 12px; border-bottom:1px solid var(--rule); vertical-align:middle}
tbody tr:last-child td{border-bottom:none}
tbody tr:hover td{background:var(--surface-2)}
td.num,th.num{text-align:right; font-family:"JetBrains Mono",monospace; font-variant-numeric:tabular-nums; white-space:nowrap}
td.nm{min-width:190px}
td.nm .co{font-weight:500}
td.nm .tk{font-family:"JetBrains Mono",monospace; font-size:11.5px; color:var(--ink-3); margin-left:7px}
tbody tr{border-left:3px solid transparent}
tbody tr.s-buy  td:first-child{box-shadow:inset 3px 0 0 var(--jade)}
tbody tr.s-hold td:first-child{box-shadow:inset 3px 0 0 var(--rule-2)}
tbody tr.s-wait td:first-child{box-shadow:inset 3px 0 0 var(--clay)}
.sect{font-size:12px; color:var(--ink-3)}
.up{color:var(--jade)} .down{color:var(--clay)} .flat{color:var(--ink-3)}
.na{color:var(--ink-3); font-style:italic; font-size:.92em; font-family:"DM Sans",sans-serif}
.tgt{display:block; font-size:12.5px}
.ups{display:block; font-size:11.5px}
.rv.g{color:var(--jade)} .rv.a{color:var(--amber)} .rv.r{color:var(--clay)}
.dval.g{color:var(--jade)} .dval.a{color:var(--amber)} .dval.r{color:var(--clay)} .dval.na{color:var(--ink-3)}
.scr{font-size:11px; font-family:"JetBrains Mono",monospace; color:var(--ink-2); white-space:nowrap}
.scr.both{color:var(--jade)}
.sco{font-weight:700; font-size:14px}

/* ---------- badges ---------- */
.badge{display:inline-block; padding:2px 8px; border-radius:2px; font-size:10.5px; font-weight:500;
       letter-spacing:.09em; text-transform:uppercase; white-space:nowrap; border:1px solid transparent}
.b-sbuy{background:var(--jade); color:var(--ground); border-color:var(--jade)}
.b-buy {background:var(--jade-soft); color:var(--jade); border-color:var(--jade-line)}
.b-hold{background:var(--surface-2); color:var(--ink-2); border-color:var(--rule-2)}
.b-wait{background:var(--amber-soft); color:var(--amber); border-color:var(--amber)}
.b-skip{background:var(--clay-soft); color:var(--clay); border-color:var(--clay)}

/* ---------- ratio explainer cards ---------- */
.rgrid{display:grid; grid-template-columns:repeat(auto-fit,minmax(232px,1fr)); gap:14px}
.rcard{background:var(--surface); border:1px solid var(--rule); border-radius:3px; padding:16px 17px;
       display:flex; flex-direction:column; gap:9px; box-shadow:var(--shadow)}
.rcard h3{font-family:"Cormorant Garamond",Georgia,serif; font-size:25px; font-weight:600; margin:0; line-height:1}
.rcard .full{font-size:10.5px; letter-spacing:.12em; text-transform:uppercase; color:var(--jade); margin-top:-4px}
.rcard p{margin:0; font-size:13px; color:var(--ink-2); line-height:1.55}
.bands{display:flex; flex-direction:column; gap:3px; margin-top:2px; border-top:1px solid var(--rule); padding-top:9px}
.bd{display:flex; align-items:center; gap:8px; font-size:11px; font-family:"JetBrains Mono",monospace; white-space:nowrap}
.sw{width:9px; height:9px; border-radius:1px; flex:0 0 auto}
.sw.g{background:var(--jade)} .sw.a{background:var(--amber)} .sw.r{background:var(--clay)}
.bd .txt{color:var(--ink-2)}

/* ---------- method box ---------- */
.method{margin-top:16px; background:var(--jade-soft); border:1px solid var(--jade-line); border-radius:3px; padding:20px 22px}
.method h3{font-family:"Cormorant Garamond",Georgia,serif; font-size:24px; margin:0 0 4px; font-weight:600}
.method p{margin:0 0 12px; font-size:13.5px; color:var(--ink-2); max-width:80ch}
.mgrid{display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:10px; margin:14px 0}
.mi{background:var(--surface); border:1px solid var(--jade-line); border-radius:2px; padding:9px 11px}
.mi .p{font-family:"JetBrains Mono",monospace; font-size:19px; color:var(--jade); font-weight:500}
.mi .n2{font-size:11.5px; color:var(--ink-2)}
.bandrow{display:flex; flex-wrap:wrap; gap:7px; margin-top:6px}
.guard{margin-top:14px; border-top:1px solid var(--jade-line); padding-top:12px}
.guard ul{margin:6px 0 0; padding-left:19px; font-size:13px; color:var(--ink-2); columns:2; column-gap:28px}
.guard li{margin-bottom:3px; break-inside:avoid}
@media(max-width:640px){.guard ul{columns:1}}

/* ---------- top picks ---------- */
.picks{display:grid; gap:14px}
.pick{background:var(--surface); border:1px solid var(--rule); border-left:3px solid var(--jade);
      border-radius:3px; padding:20px 22px; display:grid; grid-template-columns:52px 1fr; gap:20px; box-shadow:var(--shadow)}
.rank{font-family:"Cormorant Garamond",Georgia,serif; font-size:50px; line-height:.8; color:var(--jade); font-weight:600}
.pick-h{display:flex; flex-wrap:wrap; align-items:baseline; gap:11px; margin-bottom:3px}
.pick-h .nm2{font-family:"Cormorant Garamond",Georgia,serif; font-size:27px; font-weight:600; line-height:1.1}
.pick-h .tk2{font-family:"JetBrains Mono",monospace; font-size:12.5px; color:var(--ink-3)}
.pline{display:flex; flex-wrap:wrap; gap:16px; align-items:baseline; margin:8px 0 12px;
       font-family:"JetBrains Mono",monospace; font-size:13px}
.pline .px{font-size:21px; font-weight:500}
.pick p.an{margin:12px 0 0; font-size:14px; color:var(--ink-2); max-width:82ch}
.pfoot{display:flex; flex-wrap:wrap; gap:8px 20px; margin-top:13px; padding-top:11px;
       border-top:1px solid var(--rule); font-size:12px; color:var(--ink-3)}
.pfoot b{font-family:"JetBrains Mono",monospace; color:var(--ink-2); font-weight:500}

/* ---------- stock cards ---------- */
.cards{display:grid; grid-template-columns:repeat(auto-fill,minmax(348px,1fr)); gap:14px}
.card{background:var(--surface); border:1px solid var(--rule); border-radius:3px; padding:16px 18px;
      display:flex; flex-direction:column; gap:9px; box-shadow:var(--shadow); border-left:3px solid var(--rule-2)}
.card.s-buy{border-left-color:var(--jade)}
.card.s-hold{border-left-color:var(--rule-2)}
.card.s-wait{border-left-color:var(--clay)}
.chead{display:flex; align-items:flex-start; justify-content:space-between; gap:10px}
.chead .cn{font-family:"Cormorant Garamond",Georgia,serif; font-size:21px; font-weight:600; line-height:1.15}
.chead .ct{font-family:"JetBrains Mono",monospace; font-size:11.5px; color:var(--ink-3)}
.cprice{display:flex; flex-wrap:wrap; gap:13px; align-items:baseline; font-family:"JetBrains Mono",monospace; font-size:12.5px}
.cprice .p1{font-size:19px; font-weight:500}
.cprice .mc{color:var(--ink-3)}
.dash{display:grid; grid-template-columns:repeat(5,1fr); gap:1px; background:var(--rule);
      border:1px solid var(--rule); border-radius:2px; overflow:hidden}
.dcell{background:var(--surface-2); padding:6px 4px; display:flex; flex-direction:column; align-items:center; gap:1px}
.dlab{font-size:9px; letter-spacing:.09em; text-transform:uppercase; color:var(--ink-3)}
.dval{font-family:"JetBrains Mono",monospace; font-size:12.5px; font-weight:500}
.card p.an{margin:1px 0 0; font-size:13px; color:var(--ink-2); line-height:1.56}
.cfoot{margin-top:auto; padding-top:10px; border-top:1px solid var(--rule); display:flex; flex-wrap:wrap;
       gap:5px 14px; font-size:11.5px; color:var(--ink-3); font-family:"JetBrains Mono",monospace}
.cfoot span b{color:var(--ink-2); font-weight:500}
.gflag{color:var(--amber); font-size:11.5px; font-family:"DM Sans",sans-serif; font-style:italic}

/* ---------- funds ---------- */
.fcards{display:grid; grid-template-columns:repeat(auto-fill,minmax(340px,1fr)); gap:14px}
.hold{display:flex; flex-direction:column; gap:3px; margin-top:2px}
.hrow{display:flex; justify-content:space-between; gap:10px; font-size:11.5px; font-family:"JetBrains Mono",monospace;
      color:var(--ink-2); border-bottom:1px dotted var(--rule); padding-bottom:2px}
.hlab{font-size:10px; letter-spacing:.12em; text-transform:uppercase; color:var(--ink-3); margin-top:4px}

/* ---------- notes ---------- */
.ngrid{display:grid; grid-template-columns:repeat(auto-fit,minmax(290px,1fr)); gap:14px}
.ncard{background:var(--surface); border:1px solid var(--rule); border-radius:3px; padding:17px 19px; box-shadow:var(--shadow)}
.ncard h3{font-family:"Cormorant Garamond",Georgia,serif; font-size:22px; margin:0 0 8px; font-weight:600}
.ncard ul{margin:0; padding-left:18px; font-size:13.5px; color:var(--ink-2)}
.ncard li{margin-bottom:7px}
.ncard p{margin:0 0 9px; font-size:13.5px; color:var(--ink-2)}
.dq{background:var(--amber-soft); border-color:var(--amber)}
.dq h3{color:var(--amber)}
.disc{margin-top:26px; background:var(--surface-2); border:1px solid var(--rule); border-left:3px solid var(--ink-3);
      border-radius:3px; padding:17px 20px; font-size:12.5px; color:var(--ink-2); line-height:1.6}
.disc b{color:var(--ink)}
footer{margin-top:44px; padding-top:20px; border-top:1px solid var(--rule); font-size:12px; color:var(--ink-3);
       display:flex; flex-wrap:wrap; gap:10px; justify-content:space-between}
code{font-family:"JetBrains Mono",monospace; font-size:.9em; background:var(--surface-2); padding:1px 5px; border-radius:2px}
@media (prefers-reduced-motion: reduce){*{animation:none!important; transition:none!important}}
@media(max-width:560px){
  .pick{grid-template-columns:1fr; gap:8px} .rank{font-size:34px}
  .hero-in{padding:34px 22px 26px} .stamp{align-items:flex-start; text-align:left}
}
</style>
"""
