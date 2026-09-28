import os
from datetime import date, timedelta
from html import escape
from urllib.parse import urljoin

import altair as alt
import pandas as pd
import requests
import streamlit as st

from styles import CSS

API_BASE = os.getenv("PLANTCARE_API_URL", "http://localhost:4000/api").rstrip("/") + "/"
st.set_page_config(page_title="PlantCare · Garden journal", page_icon="🌿", layout="wide", initial_sidebar_state="expanded")
st.markdown(CSS, unsafe_allow_html=True)


def request(method, path, *, params=None, payload=None):
    try:
        response = requests.request(method, urljoin(API_BASE, path.lstrip("/")), params=params, json=payload, timeout=12)
        if not response.ok:
            try:
                detail = response.json().get("error", response.text)
            except ValueError:
                detail = response.text
            st.error(f"API returned {response.status_code}: {detail}")
            return None
        return response.json() if response.content else {}
    except requests.RequestException as exc:
        st.error(f"Could not reach PlantCare API at {API_BASE}. Start the Express server and try again. ({exc})")
        return None


def load_plants(params=None):
    return request("GET", "plants", params=params) or []


def fmt(value):
    if not value:
        return "Not recorded"
    try:
        return date.fromisoformat(str(value)[:10]).strftime("%-d %b %Y")
    except ValueError:
        return str(value)


def status_label(value):
    return (value or "CARE OK").upper()


def status_class(value):
    return {"OVERDUE":"late", "CARE DUE":"due", "CARE SOON":"soon", "CARE OK":"ok"}.get(status_label(value), "none")


def page_header(kicker, title, subtitle=None):
    st.markdown(f'<div class="eyebrow">{escape(str(kicker))}</div>', unsafe_allow_html=True)
    st.title(title)
    if subtitle:
        st.markdown(f'<p class="pc-sub">{escape(str(subtitle))}</p>', unsafe_allow_html=True)


def growth_chart(records, chart_height=260):
    points = [{"date":row.get("date"), "height":row.get("height"), "leaves":row.get("leafCount"), "plant":row.get("plant", "This plant")}
              for row in records if row.get("height") is not None and row.get("date")]
    if not points:
        st.caption("Growth notes will take root here.")
        return
    frame = pd.DataFrame(points)
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame = frame.dropna(subset=["date", "height"])
    line = alt.Chart(frame).encode(
        x=alt.X("date:T", title=None, axis=alt.Axis(format="%d %b", labelColor="#718075", tickColor="#DCD8CA", domain=False)),
        y=alt.Y("height:Q", title="Height (cm)", axis=alt.Axis(labelColor="#718075", gridColor="#E3E0D5", domain=False)),
        color=alt.Color("plant:N", title=None, scale=alt.Scale(range=["#3D6B4F", "#47758A", "#B7862B", "#A55E49", "#718B5A"])),
        tooltip=[alt.Tooltip("plant:N", title="Plant"), alt.Tooltip("date:T", title="Date", format="%d %b %Y"), alt.Tooltip("height:Q", title="Height (cm)"), alt.Tooltip("leaves:Q", title="Leaves")]
    )
    chart=(line.mark_line(strokeWidth=2.5, interpolate="monotone") + line.mark_circle(size=56, stroke="white", strokeWidth=1.5)).properties(height=chart_height).configure_view(strokeWidth=0).configure(background="transparent")
    st.altair_chart(chart, use_container_width=True)


def identity_form(plant=None, key="plant"):
    p = plant or {}
    with st.form(key):
        st.markdown("#### 01 · Identity")
        c1,c2 = st.columns(2)
        name = c1.text_input("Common name *", value=p.get("name", ""))
        scientific = c2.text_input("Scientific name", value=p.get("scientificName", ""))
        types = ["Houseplant","Herb","Flowering shrub","Climber","Succulent","Palm","Tree","Other"]
        plant_type = st.selectbox("Plant type", types, index=types.index(p.get("plantType")) if p.get("plantType") in types else 0)
        st.markdown("#### 02 · Environment")
        c1,c2 = st.columns(2)
        location = c1.text_input("Location *", value=p.get("location", ""), placeholder="Balcony, kitchen window…")
        environments = ["Indoor","Outdoor","Both"]
        env = c2.selectbox("Setting", environments, index=environments.index(p.get("indoorOutdoor")) if p.get("indoorOutdoor") in environments else 0)
        sun_options = ["Full sun","Morning sun","Partial sun","Bright indirect light","Indirect light","Low light"]
        sunlight = st.selectbox("Sunlight requirement", sun_options, index=sun_options.index(p.get("sunlightRequirement")) if p.get("sunlightRequirement") in sun_options else 3)
        st.markdown("#### 03 · Care & record")
        c1,c2 = st.columns(2)
        interval = c1.number_input("Water every (days) *", min_value=1, max_value=120, value=int(p.get("wateringFrequency", 7)))
        added = c2.date_input("Date added", value=date.fromisoformat(str(p.get("dateAdded", date.today().isoformat()))[:10]) if p.get("dateAdded") else date.today())
        image = st.text_input("Image URL · optional", value=p.get("image", ""))
        notes = st.text_area("Notes", value=p.get("notes", ""), placeholder="Where it came from, what you have noticed…")
        submitted = st.form_submit_button("Save plant record" if plant else "Add to my garden")
    if submitted:
        if not name.strip() or not location.strip():
            st.error("Common name and location are required.")
            return False
        payload = {"name":name.strip(),"scientificName":scientific.strip(),"plantType":plant_type,"location":location.strip(),"indoorOutdoor":env,"sunlightRequirement":sunlight,"wateringFrequency":interval,"dateAdded":added.isoformat(),"image":image.strip(),"notes":notes.strip()}
        result = request("PUT" if plant else "POST", f"plants/{plant['_id']}" if plant else "plants", payload=payload)
        if result:
            st.session_state["plantcare_detail_id"] = result.get("_id", plant.get("_id") if plant else None)
            st.session_state["plantcare_pending_nav"] = "Plant record"
            st.session_state["plantcare_flash"] = (f"{payload['name']} was added to your garden and saved to MongoDB." if not plant else f"{payload['name']}’s record was updated.", "🌱")
            st.rerun()
    return submitted


def dashboard():
    data = request("GET", "dashboard")
    if not data:
        return
    stats = data.get("stats", {})
    page_header(f"{date.today().strftime('%A, %-d %B %Y')} · Monsoon notes", "A good day to tend to things.", "Your garden, as it is today.")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Garden overview", f"{stats.get('totalPlants',0):02d}", "plants in your care")
    c2.metric("Watering due", f"{stats.get('wateringDue',0):02d}", "plants need a drink")
    c3.metric("Fertilizer soon", f"{stats.get('fertilizerDue',0):02d}", "feed in the coming days")
    c4.metric("Health watch", f"{stats.get('activeHealthIssues',0):02d}", "being observed")
    st.divider()
    left,right=st.columns([1.2,.8],gap="large")
    with left:
        st.markdown('<div class="eyebrow">THE NEXT FEW DAYS</div>',unsafe_allow_html=True)
        st.subheader("Today's care")
        urgency={"OVERDUE":0,"CARE DUE":1,"CARE SOON":2}
        due=[p for p in data.get("plants",[]) if p.get("care",{}).get("status") in urgency]
        due.sort(key=lambda p:(urgency[p["care"]["status"]],p["name"]))
        if due:
            for p in due[:7]:
                care=p.get("care",{})
                label="Water overdue" if care.get("status")=="OVERDUE" else "Water today" if care.get("status")=="CARE DUE" else "Care soon"
                if care.get("nextFertilizer") and str(care["nextFertilizer"])[:10] <= (date.today()+timedelta(days=4)).isoformat(): label="Fertilizer due soon"
                with st.container(border=True):
                    a,b,c=st.columns([2,2,1]); a.markdown(f"**{escape(str(p['name']))}**  \n{escape(str(p.get('location','')))}");b.write(label);c.markdown(f'<span class="tag {status_class(care.get("status"))}">{escape(status_label(care.get("status")))}</span>',unsafe_allow_html=True)
        else: st.info("A quiet day in the garden. Everything is tended.")
    with right:
        st.markdown('<div class="eyebrow">OVER THE PAST WEEKS</div>',unsafe_allow_html=True)
        st.subheader("Growth, recorded")
        growth=data.get("growthSnapshot",[])
        if growth:
            growth_chart(growth, chart_height=240)
            st.caption("HEIGHT IN CM · FIELD MEASUREMENTS")
        else: st.caption("Growth notes will take root here.")
    st.divider()
    st.markdown('<div class="eyebrow">FROM THE NOTEBOOK</div>',unsafe_allow_html=True);st.subheader("Recent activity")
    activity=data.get("activity",[])
    if activity:
        for index,row in enumerate(activity[:8]):
            plant_name=escape(str(row.get("plant","Plant")))
            summary=escape(str(row.get("summary","Care note")))
            kind=escape(str(row.get("type","")).title())
            st.markdown(f'<div class="pc-entry" style="--delay:{index*45}ms"><b>{plant_name}</b> · {summary}<small>{fmt(row.get("date"))} · {kind}</small></div>',unsafe_allow_html=True)
    else: st.caption("Your garden's story starts with the first note.")


def go_to_record(plant_id):
    st.session_state["plantcare_detail_id"] = plant_id
    st.session_state["plantcare_nav"] = "Plant record"


def collection():
    page_header("The living collection", "My plants.", "A botanical catalogue of the things in your care.")
    with st.container(border=True):
        c1,c2,c3=st.columns([2,1,1]); search=c1.text_input("Search plants",placeholder="Find a plant, place…",label_visibility="collapsed"); typ=c2.selectbox("Plant type",["All types","Herb","Houseplant","Climber","Succulent","Flowering shrub","Palm","Tree"]); env=c3.selectbox("Setting",["All settings","Indoor","Outdoor","Both"])
        c4,c5,c6=st.columns(3); sun=c4.selectbox("Sunlight",["All sunlight","Full sun","Partial sun","Indirect","Low"]); state=c5.selectbox("Care state",["All care states","CARE OK","CARE SOON","CARE DUE","OVERDUE"]); sort=c6.selectbox("Sort",["Name A—Z","Recently added","Oldest first"])
    params={"search":search,"type":typ if typ!="All types" else "","environment":env if env!="All settings" else "","sunlight":sun if sun!="All sunlight" else "","status":state if state!="All care states" else "","sort":{"Name A—Z":"name","Recently added":"newest","Oldest first":"oldest"}[sort]}
    plants=load_plants({k:v for k,v in params.items() if v})
    st.caption(f"{len(plants)} botanical record{'s' if len(plants)!=1 else ''}")
    if not plants: st.info("No plants match these notes. Adjust your filters or add a new record.")
    cols=st.columns(3)
    for i,p in enumerate(plants):
        with cols[i%3]:
            with st.container(border=True):
                if p.get("image"):
                    st.image(p["image"],use_container_width=True)
                else:
                    st.markdown(f"<div class='specimen'><span class='eyebrow'>SPECIMEN · {i+1:02d}</span><h3>{escape(str(p['name']))}</h3><i>{escape(str(p.get('scientificName','')))}</i><br/><span class='small-note'>{escape(str(p.get('location','')))}</span></div>",unsafe_allow_html=True)
                st.markdown(f"### {escape(str(p['name']))}")
                st.caption(p.get("scientificName") or p.get("plantType","Plant"))
                care_status=p.get("care",{}).get("status","CARE OK")
                st.markdown(f'<span class="tag {status_class(care_status)}">{escape(status_label(care_status))}</span> &nbsp; {escape(str(p.get("location","")))}',unsafe_allow_html=True)
                st.caption(f"{p.get('sunlightRequirement','')} · Water every {p.get('wateringFrequency','?')} days")
                open_col, remove_col = st.columns([3,1])
                open_col.button("Open record →",key=f"open_{p['_id']}",use_container_width=True,on_click=go_to_record,args=(p["_id"],))
                if remove_col.button("Remove",key=f"remove_{p['_id']}",help="Delete this plant and all of its care history in one click"):
                    deleted=request("DELETE",f"plants/{p['_id']}")
                    if deleted is not None:
                        st.session_state["plantcare_flash"]=(f"{p['name']} and its care history were removed.","🗑️")
                        st.rerun()


def detail_page(plant_id):
    detail=request("GET",f"plants/{plant_id}")
    if not detail:return
    p=detail["plant"];care=detail["care"]
    page_header(f"{p.get('location','').upper()} · {p.get('indoorOutdoor','').upper()}",p["name"],p.get("scientificName",""))
    st.caption(f"{p.get('plantType','')} · {p.get('sunlightRequirement','')} · Water every {p.get('wateringFrequency')} days · {care.get('status','CARE OK')}")
    st.write(p.get("notes") or "A new entry in the garden journal.")
    c1,c2,c3,c4=st.columns(4);c1.metric("Last watered",fmt(care.get("lastWatered")));c2.metric("Next watering",fmt(care.get("nextWatering")));c3.metric("Last fertilizer",fmt(care.get("lastFertilizer")));c4.metric("Health watch",care.get("activeHealthIssues",0))
    with st.expander("Edit plant identity and care details"):
        identity_form(p,key=f"edit_{p['_id']}")
    with st.expander("Remove plant record"):
        st.warning("Removing a plant also removes its watering, fertilizer, health and growth history.")
        confirm=st.checkbox(f"I want to remove {p['name']} and its care history",key=f"confirm_{p['_id']}")
        if st.button("Delete plant",disabled=not confirm,key=f"delete_{p['_id']}"):
            if request("DELETE",f"plants/{plant_id}") is not None:
                st.success("Plant record removed.");st.session_state.pop("plantcare_detail_id",None);st.rerun()
    st.divider();st.markdown('<div class="eyebrow">ADD TO THE JOURNAL</div>',unsafe_allow_html=True);st.subheader("Record care")
    tabs=st.tabs(["Watering","Fertilizer","Health","Growth"])
    today=date.today().isoformat()
    with tabs[0]:
        with st.form(f"water_{plant_id}"):
            d=st.date_input("Date",value=date.today());amount=st.text_input("Amount / method",value="Soil moistening");note=st.text_input("Observation");ok=st.form_submit_button("Save watering note")
        if ok and request("POST","watering",payload={"plantId":plant_id,"date":d.isoformat(),"amount":amount,"notes":note}) is not None: st.success("Watering note recorded.");st.rerun()
    with tabs[1]:
        with st.form(f"fert_{plant_id}"):
            n=st.text_input("Fertilizer name *");d=st.date_input("Date applied",value=date.today(),key=f"fd_{plant_id}");q=st.text_input("Quantity");nextd=st.date_input("Next application",value=date.today(),key=f"fnext_{plant_id}");note=st.text_input("Observation",key=f"fnote_{plant_id}");ok=st.form_submit_button("Save fertilizer note")
        if ok and n.strip() and request("POST","fertilizer",payload={"plantId":plant_id,"fertilizerName":n,"dateApplied":d.isoformat(),"quantity":q,"nextApplication":nextd.isoformat(),"notes":note}) is not None: st.success("Fertilizer note recorded.");st.rerun()
    with tabs[2]:
        with st.form(f"health_{plant_id}"):
            issue=st.text_input("Issue type *");symptoms=st.text_area("Symptoms");d=st.date_input("Date noticed",value=date.today(),key=f"hd_{plant_id}");treatment=st.text_area("Treatment");state=st.selectbox("Status",["Active","Monitoring","Resolved"]);note=st.text_input("Additional notes");ok=st.form_submit_button("Save health note")
        if ok and issue.strip() and request("POST","health",payload={"plantId":plant_id,"issueType":issue,"symptoms":symptoms,"detectedDate":d.isoformat(),"treatment":treatment,"status":state,"notes":note}) is not None: st.success("Health note recorded.");st.rerun()
    with tabs[3]:
        with st.form(f"growth_{plant_id}"):
            d=st.date_input("Measurement date",value=date.today(),key=f"gd_{plant_id}");height=st.number_input("Height · cm",min_value=0.0,step=0.5);leaves=st.number_input("Leaf count",min_value=0,step=1);observation=st.text_input("Observation");ok=st.form_submit_button("Save growth note")
        if ok and request("POST","growth",payload={"plantId":plant_id,"date":d.isoformat(),"height":height,"leafCount":leaves,"observation":observation}) is not None: st.success("Growth note recorded.");st.rerun()
    st.divider();t1,t2,t3=st.tabs(["Care history","Growth","Health"])
    with t1:
        entries=[]
        for kind,field,title in [("watering","date","Watering"),("fertilizer","dateApplied","Fertilizer"),("health","detectedDate","Health"),("growth","date","Growth")]:
            for row in detail.get(kind,[]): entries.append((row.get(field,""),title,row))
        entries.sort(key=lambda x:x[0],reverse=True)
        if entries:
            for dt,title,row in entries:
                with st.container(border=True):
                    content, remove = st.columns([5,1])
                    content.caption(f"{title.upper()} · {fmt(dt)}")
                    content.write(row.get("amount") or row.get("fertilizerName") or row.get("issueType") or f"{row.get('height','—')} cm · {row.get('leafCount','—')} leaves")
                    content.caption(row.get("notes") or row.get("observation") or row.get("symptoms") or row.get("treatment") or "")
                    endpoint={"Watering":"watering","Fertilizer":"fertilizer","Health":"health","Growth":"growth"}[title]
                    if remove.button("Remove",key=f"remove_{endpoint}_{row['_id']}"):
                        if request("DELETE",f"{endpoint}/{row['_id']}") is not None: st.success("Journal entry removed.");st.rerun()
        else:st.info("The first care note is waiting to be written.")
    with t2:
        growth=detail.get("growth",[])
        if growth:growth_chart([{**x,"plant":p["name"]} for x in growth],chart_height=280)
        else:st.info("Add growth notes to see this plant’s progress.")
    with t3:
        records=detail.get("health",[])
        if records:
            for row in records:
                with st.container(border=True):st.caption(f"{row.get('status','').upper()} · {fmt(row.get('detectedDate'))}");st.subheader(row.get("issueType","Health observation"));st.write(row.get("symptoms",""));st.caption(f"Treatment: {row.get('treatment','Not recorded')}")
        else:st.info("No health concerns recorded. Keep observing.")


def history_page():
    page_header("The garden’s memory", "Care history.", "Every small act, kept in one place.")
    plants=load_plants()
    c1,c2,c3,c4=st.columns([1.4,1,1,1]); plant=c1.selectbox("Plant",["All plants"]+[p["name"] for p in plants]);kind=c2.selectbox("Activity",["All activity","Watering","Fertilizer","Health","Growth"]);from_date=c3.date_input("From",value=None);to_date=c4.date_input("To",value=None)
    plant_id=next((p["_id"] for p in plants if p["name"]==plant),None)
    types={"Watering":"watering","Fertilizer":"fertilizer","Health":"health","Growth":"growth"};selected=[types[kind]] if kind in types else list(types.values())
    rows=[]
    for item in selected:
        params={}
        if plant_id:params["plantId"]=plant_id
        if from_date:params["from"]=from_date.isoformat()
        if to_date:params["to"]=to_date.isoformat()
        result=request("GET",item,params=params) or []
        field={"watering":"date","fertilizer":"dateApplied","health":"detectedDate","growth":"date"}[item]
        for row in result:
            rows.append((row.get(field,""),item,row))
    rows.sort(key=lambda r:r[0],reverse=True)
    if not rows:st.info("No journal entries match this selection.")
    for dt,item,row in rows:
        pname=(row.get("plantId") or {}).get("name","Plant")
        note=row.get("amount") or row.get("fertilizerName") or row.get("issueType") or f"{row.get('height','—')} cm · {row.get('leafCount','—')} leaves"
        with st.container(border=True):
            a,b,c=st.columns([1,1,2]);a.caption(fmt(dt));b.write(f"**{item.title()}** · {pname}");c.write(note)


with st.sidebar:
    st.markdown('<div class="pc-brand">PlantCare</div><div class="pc-brand-sub">A living garden journal</div><div class="pc-edition">FIELD NOTES · № 01 / 2026</div>',unsafe_allow_html=True)
    if "plantcare_pending_nav" in st.session_state:
        st.session_state["plantcare_nav"] = st.session_state.pop("plantcare_pending_nav")
    if "plantcare_flash" in st.session_state:
        message, icon = st.session_state.pop("plantcare_flash")
        st.toast(message, icon=icon)
    nav=st.radio("Your garden",["Overview","My plants","Add a plant","Care history","Plant record"],key="plantcare_nav",label_visibility="visible")
    st.divider();st.markdown("✳ **GROWING SEASON**  \nMonsoon · 2026  \nSouth India")

if nav=="Overview": dashboard()
elif nav=="My plants": collection()
elif nav=="Add a plant":
    page_header("Botanical record · identity & care", "Add to the collection.", "A few details help you notice what each plant needs.")
    identity_form()
elif nav=="Care history": history_page()
elif nav=="Plant record":
    plants=load_plants();options={p["name"]:p["_id"] for p in plants};ids=list(options.values());current=st.session_state.get("plantcare_detail_id");index=ids.index(current) if current in ids else 0
    if options:
        chosen=st.selectbox("Choose a plant",list(options),index=index)
        st.session_state.plantcare_detail_id=options[chosen]
        detail_page(options[chosen])
    else:st.info("Add your first plant to open its botanical record.")
