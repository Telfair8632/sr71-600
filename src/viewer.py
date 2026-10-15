from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
data=(ROOT/'data'/'meshes.json').read_text(encoding='utf-8')
html=(ROOT/'src'/'viewer_template.html').read_text(encoding='utf-8').replace('__DATA__',data)
(ROOT/'model_preview.html').write_text(html,encoding='utf-8')
(ROOT/'qa'/'viewer_script.js').write_text(html.split('<script>')[1].split('</script>')[0],encoding='utf-8')
print('Offline WebGL viewer generated')
