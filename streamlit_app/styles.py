"""PlantCare's botanical editorial theme and motion system."""

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Manrope:wght@400;500;600;700&display=swap');
:root{--paper:#F5F2E9;--card:#FFFEFA;--ink:#243129;--muted:#718075;--line:#DCD8CA;--forest:#213D2D;--moss:#3D6B4F;--sage:#E4EBDD;--water:#47758A;--clay:#A55E49;--ochre:#B7862B;--rose:#93495B}
.stApp{background:var(--paper);color:var(--ink);font-family:'Manrope',system-ui,sans-serif}
.block-container{padding-top:2.2rem;padding-bottom:3rem;max-width:1320px}
html,body,[class*="css"]{font-family:'Manrope',system-ui,sans-serif}
h1,h2,h3,h4{font-family:'Fraunces',Georgia,serif!important;font-weight:500!important;letter-spacing:-.02em;color:var(--ink)}
h1{font-size:clamp(2.5rem,4vw,3.5rem)!important;line-height:1.04!important;position:relative;padding-bottom:.55rem;animation:fieldTitle .62s cubic-bezier(.2,.8,.2,1) both}
h1::after{content:"";position:absolute;left:0;bottom:0;width:58px;height:2px;background:var(--moss);transform-origin:left;animation:drawRule .72s .12s cubic-bezier(.2,.8,.2,1) both}
h2{font-size:1.8rem!important}h3{font-size:1.4rem!important}
p,li{line-height:1.7}
[data-testid="stSidebar"]{background:linear-gradient(165deg,#244532 0%,#1C3426 62%,#192D21 100%);border-right:1px solid #183021}
[data-testid="stSidebar"] *{color:#EFF2E8}
[data-testid="stSidebar"] h1{font-family:'Fraunces',Georgia,serif!important;color:#F5F2E9!important}
[data-testid="stSidebar"] [role="radiogroup"] label{padding:.48rem .55rem;border-radius:3px;transition:background .2s ease,transform .2s ease}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:#ffffff12;transform:translateX(3px)}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{color:#CFD8CC}
.pc-brand{font:600 1.8rem 'Fraunces',Georgia,serif;letter-spacing:-.03em;color:#F5F2E9;margin:0 0 .1rem}
.pc-brand-sub{font-size:.73rem;letter-spacing:.04em;color:#B8C8B7!important;margin-bottom:1.35rem}
.pc-edition{font-size:.62rem;font-weight:700;letter-spacing:.17em;color:#C4D0C1!important;text-transform:uppercase}
.eyebrow{letter-spacing:.16em;text-transform:uppercase;color:#788573;font-size:.66rem;font-weight:700}
[data-testid="stMetric"]{background:#EAEADF;border:1px solid #D5D4C8;padding:1rem 1.15rem;min-height:118px;border-radius:3px;animation:metricSettle .55s cubic-bezier(.2,.8,.2,1) both;transition:border-color .2s ease,background .2s ease}
[data-testid="stMetric"]:hover{border-color:#AAB8A4;background:#EFEFE5}
[data-testid="stMetricLabel"]{font-size:.67rem!important;letter-spacing:.12em;text-transform:uppercase;color:#718075!important}
[data-testid="stMetricValue"]{font-family:'Fraunces',Georgia,serif;color:var(--forest);font-weight:500}
[data-testid="stMetricDelta"]{font-size:.72rem}
[data-testid="stVerticalBlockBorderWrapper"]{background:var(--card);border:1px solid var(--line)!important;border-radius:4px!important;transition:transform .24s ease,border-color .24s ease,box-shadow .24s ease,background-color .24s ease}
[data-testid="stVerticalBlockBorderWrapper"]:hover{border-color:#B6C1AF!important;box-shadow:0 12px 27px -20px #18291e66;transform:translateY(-2px)}
.stButton>button,.stFormSubmitButton>button{border-radius:3px;border:1px solid var(--forest);background:var(--forest);color:#F5F2E9;font-weight:600;transition:background .2s,color .2s,border-color .2s,transform .16s,box-shadow .2s}
.stButton>button:hover,.stFormSubmitButton>button:hover{background:#31533C;color:white;border-color:#31533C;transform:translateY(-1px);box-shadow:0 7px 16px -11px #20392a99}
.stButton>button:active,.stFormSubmitButton>button:active{transform:translateY(1px);box-shadow:none}
.stTextInput input,.stTextArea textarea,.stNumberInput input,.stDateInput input,.stSelectbox div[data-baseweb="select"]>div,.stMultiSelect div[data-baseweb="select"]>div{border-radius:2px;background:#FFFEFA;border-color:#CBC9BC}
.stTextInput input:focus,.stTextArea textarea:focus,.stNumberInput input:focus{border-color:var(--moss);box-shadow:0 0 0 1px var(--moss)}
.stTabs [data-baseweb="tab-list"]{gap:1.2rem;border-bottom:1px solid var(--line)}
.stTabs [data-baseweb="tab"]{background:transparent;color:var(--muted)}
.stTabs [aria-selected="true"]{color:var(--forest)!important}
.stAlert{border-radius:3px}
[data-testid="stToast"]{border-left:3px solid var(--moss);border-radius:2px!important;box-shadow:0 9px 26px #1d302019}
hr{border-color:var(--line)}
.specimen{padding:1.2rem 1.25rem;border-left:2px solid #93A18A;background:#EDEDE2;margin:.2rem 0 .7rem;min-height:132px;transition:background .25s ease,border-color .25s ease}
[data-testid="stVerticalBlockBorderWrapper"]:hover .specimen{background:#E7EBDD;border-color:var(--moss)}
.specimen .eyebrow{font-size:.6rem}.specimen h3{margin:.5rem 0 .05rem}.specimen i{color:var(--muted);font-family:'Fraunces',Georgia,serif}
.small-note{font-size:.76rem;color:var(--muted)}
.pc-sub{color:var(--muted);margin:-.15rem 0 1.35rem}
.pc-empty{text-align:center;color:var(--muted);padding:2.2rem;border:1px dashed var(--line);background:#FFFEFA99}
.tag{display:inline-block;border-radius:99px;padding:3px 10px;font-size:.68rem;font-weight:700;letter-spacing:.035em;white-space:nowrap}
.tag.ok{background:var(--sage);color:#2D5A3E}.tag.soon{background:#EEF0E6;color:#626B42}.tag.due{background:#F6E8C9;color:#7C581A}.tag.late{background:#F3DDE0;color:#852F46}.tag.none{background:#ECE9DF;color:var(--muted)}
.pc-entry{position:relative;margin:0 0 .8rem 1.15rem;padding:.75rem .9rem;background:var(--card);border:1px solid var(--line);animation:journalEntry .42s both;animation-delay:var(--delay,0s)}
.pc-entry::before{content:"";position:absolute;left:-1.3rem;top:1rem;width:.55rem;height:.55rem;border-radius:50%;background:var(--dot,var(--moss));box-shadow:0 0 0 4px var(--paper)}
.pc-entry::after{content:"";position:absolute;left:-1.04rem;top:1.55rem;bottom:-.95rem;width:1px;background:var(--line)}
.pc-entry:last-child::after{display:none}.pc-entry b{font-family:'Fraunces',Georgia,serif;font-weight:500}.pc-entry small{display:block;color:var(--muted);font-size:.72rem}
.pc-row{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:.75rem 0;border-bottom:1px solid var(--line);animation:journalEntry .4s both;animation-delay:var(--delay,0s)}.pc-row:last-child{border:0}
@keyframes fieldTitle{from{opacity:0;transform:translateY(7px);clip-path:inset(0 0 16% 0)}to{opacity:1;transform:none;clip-path:inset(0)}}
@keyframes drawRule{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes metricSettle{from{opacity:.35;transform:translateY(5px)}to{opacity:1;transform:none}}
@keyframes journalEntry{from{opacity:0;transform:translateY(7px)}to{opacity:1;transform:none}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;animation-delay:0s!important;transition-duration:.01ms!important}}
</style>"""
