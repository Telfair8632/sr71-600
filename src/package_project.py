from pathlib import Path
import json,csv,hashlib,zipfile,datetime
from design import config,calculate,bom
ROOT=Path(__file__).resolve().parents[1];p=config();a=calculate(p)
names=['3mm paperless foam: wing, chines, central fuselage','2mm foam: nacelles and finish parts','4/2mm carbon tube main spar 380mm','2mm carbon rod 215mm x2','Thin plywood: tray, bulkheads, firewalls','PETG local printed parts','EX1103 KV11000 motors x2','2-inch 2023-series CW/CCW props and spares','15A/2S/conventional PWM BEC-less ESCs x2','2S 550mAh battery: buy two packs, only one installed','5V/3A standalone BEC','RadioMaster RP1 V2 receiver','Raspberry Pi Pico 2, no wireless, no pin headers','IWT603 and TTL harness','AHCT125 buffers, decoupling parts and lightweight solder board','EMAX ES9051-class micro servos x2','Pushrods, control horns, hinge tape','Wire, XT30, straps and heat-shrink','Glue, skid wear layer','Light finish, cockpit and identification markings','Onboard mass growth reserve (not a purchased item)','Removable steel ballast','Pocket ELRS transmitter and transmitter cells','Balance charger and power supply','Power meter, scale, thrust stand materials','Pico data USB cable and soldering consumables']
rows=bom(p)
lines=['# First-Round Procurement Budget List','','All amounts are budget allowances; no orders have been placed with vendors, so nothing here is a live quote. Buy sample units first for the prototype; verify dimensions, mass and electrical protocols first.','','| Item | Total budget / CNY | Onboard mass budget / g | Key requirements |','|---|---:|---:|---|']
for name,row in zip(names,rows):
    lines.append(f"| {row['id']} {name} | {row['budget_cny']} | {row['total_mass_g']:.2f} | {row['basis']} |")
lines+=['',f"First-round total **CNY {a['estimated_purchase_cny']}**; overall cap CNY 5000, reserve **CNY {5000-a['estimated_purchase_cny']}**.",'','ESCs, BEC, servos and battery are pre-screened by parameters only; specific vendor models are not locked yet. The 15A ESCs must support 50Hz conventional PWM; do not buy DShot-only models based on the current rating alone.','Motor thread holes, mounting screws and prop-shaft fits are verified once the actual hardware arrives; do not machine the final hole patterns before that verification.']
(ROOT/'data'/'procurement_budget.md').write_text('\n'.join(lines),encoding='utf-8')
sources=[]
from manual_content import SECTIONS
for text in SECTIONS[-1][1][:6]:
    sources.append(dict(description=text.split('https://')[0],url='https://'+text.split('https://')[1],accessed='2026-09-11'))
(ROOT/'references'/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
tasks=[
('D01','Digital design and deliverables','DONE','CAD, calculations, drawings and test record templates'),
('D02','Material and equipment interface measurement','TODO','Hole patterns, screws, prop shaft, servo and battery dimensions'),
('D03','Structural sample testing','TODO','Load/deflection/residual set, close out defects'),
('D04','Powerplant bench test','TODO','Thrust, current, temperature rise, voltage sag, consistency'),
('D05','Dry-fit assembly, mass and CG','TODO','Update BOM and CG from the actual equipment'),
('D06','Electrical and lost link','TODO','Three lost-link cases, bus loading, directions, range'),
('D07','Field and launch operations plan','TODO','School permission, airspace, local requirements, assisted takeoff validation'),
('D08','Unpowered trim','TODO','Experienced pilot judges stability and trim'),
('D09','First powered flight test','TODO','Short pattern, conservative timing, issue logging'),
('D10','Three-flight acceptance','TODO','Close out issues, bump the revision'),
('D11','1400mm new version','DEFERRED','Separate budget and design after the small version passes')]
track=ROOT/'data'/'project_task_list.md'
if not track.exists():track.write_text('# Project Task List\n\n|ID|Task|Status|Acceptance/Notes|\n|---|---|---|---|\n'+'\n'.join('| '+' | '.join(t)+' |' for t in tasks),encoding='utf-8')
files=[]
for folder in ['cad','print','cut','docs','config','src','data','references']:
    for file in sorted((ROOT/folder).rglob('*')):
        if file.is_file() and '__pycache__' not in file.parts and file.suffix.lower() not in ['.fcstd1','.fcbak'] and file.name!='manifest.json':
            data=file.read_bytes();files.append(dict(path=str(file.relative_to(ROOT)),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
manifest=dict(revision=p['revision'],created_local=datetime.datetime.now().isoformat(),flight_release=False,files=files,physical_tests='NOT PERFORMED',runtime='FreeCAD 1.1.3 / Python 3.11; artifact Python 3.12')
(ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
zip_path=ROOT.parent/'sr71_600_package.zip'
extras=[f for f in [ROOT.parent/'README.md',ROOT.parent/'build.ps1',ROOT.parent/'v2_1400'/'README.md'] if f.exists()]
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for file in extras:
        z.write(file,file.relative_to(ROOT.parent))
    for file in ROOT.rglob('*'):
        if not file.is_file() or '__pycache__' in file.parts or file.suffix.lower() in ['.fcstd1','.fcbak']:continue
        if 'qa' in file.parts and file.suffix not in ['.json']:continue
        z.write(file,file.relative_to(ROOT.parent))
print('Packaged',len(files),'files;',zip_path.name)
