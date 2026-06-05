/* ─── VintageLab App JS ─────────────────────────────────────────────────── */
'use strict';

/* ── State ─────────────────────────────────────────────────────────────── */
const S = {
  file: null,            // uploaded file data from API
  originalSrc: null,     // blob URL of uploaded file for preview
  filters: [],           // all filters from API
  selectedCam: null,     // filter id
  outputFilename: null,  // processed file name
  jobId: null,           // video job id
  jobTimer: null,
  isVideo: false,
  comparing: false,
  processing: false,
};

/* ── DOM ────────────────────────────────────────────────────────────────── */
const g = id => document.getElementById(id);
const uploadZone     = g('uploadZone');
const fileInput      = g('fileInput');
const uploadInner    = g('uploadInner');
const uploadProg     = g('uploadProg');
const progRing       = g('progRing');
const progPct        = g('progPct');
const mediaPreview   = g('mediaPreview');
const previewImg     = g('previewImg');
const previewVideo   = g('previewVideo');
const processingOv   = g('processingOverlay');
const procLabel      = g('procLabel');
const procBarWrap    = g('procBarWrap');
const procFill       = g('procFill');
const procPct        = g('procPct');
const hudTop         = g('hudTop');
const hudFilterName  = g('hudFilterName');
const btnCompare     = g('btnCompare');
const btnNewMedia    = g('btnNewMedia');
const baWrap         = g('baWrap');
const baAfterClip    = g('baAfterClip');
const baHandle       = g('baHandle');
const baBefore       = g('baBefore');
const baAfter        = g('baAfter');
const catTabs        = g('catTabs');
const camRow         = g('camRow');
const actionUpload   = g('actionUpload');
const actionDownload = g('actionDownload');
const actionPlaceholder = g('actionPlaceholder');
const dlLink         = g('dlLink');
const toastWrap      = g('toastWrap');

/* ── Toast ──────────────────────────────────────────────────────────────── */
function toast(msg, type='info', ms=3000) {
  const el = document.createElement('div');
  el.className = `toast toast-${type === 'error' ? 'err' : type === 'success' ? 'ok' : 'info'}`;
  el.textContent = msg;
  toastWrap.appendChild(el);
  setTimeout(() => { el.style.opacity='0'; el.style.transition='opacity 0.3s'; setTimeout(()=>el.remove(),300); }, ms);
}

/* ── Progress ring ──────────────────────────────────────────────────────── */
function setRing(pct) {
  const c = 169.6;
  progRing.style.strokeDashoffset = c - (pct/100)*c;
  progPct.textContent = pct + '%';
}

/* ── Upload ─────────────────────────────────────────────────────────────── */
uploadZone.addEventListener('click', () => fileInput.click());
uploadZone.addEventListener('keydown', e => { if(e.key==='Enter'||e.key===' ') fileInput.click(); });
uploadZone.addEventListener('dragover', e => { e.preventDefault(); uploadZone.classList.add('drag-over'); });
uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));
uploadZone.addEventListener('drop', e => {
  e.preventDefault(); uploadZone.classList.remove('drag-over');
  if(e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
});
fileInput.addEventListener('change', () => { if(fileInput.files[0]) handleFile(fileInput.files[0]); });
actionUpload.addEventListener('click', () => fileInput.click());

function handleFile(file) {
  const ext = file.name.split('.').pop().toLowerCase();
  const ok = ['jpg','jpeg','png','heic','heif','webp','mp4','mov','avi'];
  if(!ok.includes(ext)) { toast(`File type .${ext} not supported`, 'error'); return; }
  if(file.size > 200*1024*1024) { toast('File too large (max 200MB)', 'error'); return; }
  doUpload(file);
}

function doUpload(file) {
  uploadInner.classList.add('hidden');
  uploadProg.classList.remove('hidden');
  setRing(0);
  // Preview immediately (before/after)
  if(S.originalSrc) URL.revokeObjectURL(S.originalSrc);
  S.originalSrc = URL.createObjectURL(file);
  S.isVideo = ['mp4','mov','avi'].includes(file.name.split('.').pop().toLowerCase());

  const fd = new FormData();
  fd.append('file', file);
  const xhr = new XMLHttpRequest();
  xhr.open('POST', '/api/upload');
  xhr.upload.onprogress = e => { if(e.lengthComputable) setRing(Math.round(e.loaded/e.total*90)); };
  xhr.onload = () => {
    setRing(100);
    setTimeout(() => {
      uploadProg.classList.add('hidden');
      uploadInner.classList.remove('hidden');
      if(xhr.status === 200) {
        S.file = JSON.parse(xhr.responseText);
        showMedia();
      } else {
        let err = 'Upload failed';
        try { err = JSON.parse(xhr.responseText).error || err; } catch(_){}
        toast(err, 'error');
      }
    }, 350);
  };
  xhr.onerror = () => { uploadProg.classList.add('hidden'); uploadInner.classList.remove('hidden'); toast('Upload failed','error'); };
  xhr.send(fd);
}

function showMedia() {
  uploadZone.classList.add('hidden');
  mediaPreview.classList.remove('hidden');
  if(S.isVideo) {
    mediaPreview.classList.add('video-mode');
    previewVideo.src = S.originalSrc;
  } else {
    mediaPreview.classList.remove('video-mode');
    previewImg.src = S.originalSrc;
  }
  processingOv.classList.add('hidden');
  baWrap.classList.add('hidden');
  hudTop.style.display = 'flex';
  hudFilterName.textContent = 'Select a filter';
  actionDownload.classList.add('hidden');
  actionPlaceholder.classList.remove('hidden');
  S.outputFilename = null;
  S.comparing = false;
}

/* ── Filter loading ─────────────────────────────────────────────────────── */
let filtersLoaded = false;
async function loadFilters() {
  if(filtersLoaded) return;
  try {
    const res = await fetch('/api/filters');
    const data = await res.json();
    S.filters = data.filters;
    filtersLoaded = true;
    renderCams(currentCat());
  } catch(e) { toast('Could not load cameras','error'); }
}
loadFilters();

function currentCat() {
  return document.querySelector('.cat-tab.active')?.dataset.cat || 'Video';
}

catTabs.addEventListener('click', e => {
  const btn = e.target.closest('.cat-tab');
  if(!btn) return;
  document.querySelectorAll('.cat-tab').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  renderCams(btn.dataset.cat);
});

function renderCams(cat) {
  const list = S.filters.filter(f=>f.category===cat);
  camRow.innerHTML = '';
  list.forEach(f => {
    const card = document.createElement('div');
    card.className = 'cam-card' + (S.selectedCam===f.id?' selected':'');
    card.dataset.id = f.id;
    card.setAttribute('role','option');
    card.setAttribute('aria-selected', S.selectedCam===f.id?'true':'false');
    const isR = f.name.endsWith(' R');
    card.innerHTML = `
      <div class="cam-thumb">
        <span class="cam-thumb-emoji">${f.emoji||'📷'}</span>
        ${isR?`<span class="cam-badge">R</span>`:''}
      </div>
      <span class="cam-label">${f.name}</span>
    `;
    card.addEventListener('click', () => selectCam(f.id, f.name));
    camRow.appendChild(card);
  });
}

function selectCam(id, name) {
  if (S.selectedCam === id) return;
  S.selectedCam = id;
  document.querySelectorAll('.cam-card').forEach(c=>{
    const sel = c.dataset.id===id;
    c.classList.toggle('selected',sel);
    c.setAttribute('aria-selected',sel?'true':'false');
  });
  hudFilterName.textContent = name;
  if (S.file && !S.processing) {
    processMedia();
  }
}

/* ── Filter apply / Process ───────────────────────────────────────────────── */
async function processMedia() {
  if(!S.file) { toast('Load a photo or video first','error'); return; }
  if(!S.selectedCam) { toast('Select a camera filter first','error'); return; }
  S.processing = true;
  S.outputFilename = null;
  S.comparing = false;
  baWrap.classList.add('hidden');
  actionDownload.classList.add('hidden');

  processingOv.classList.remove('hidden');
  procLabel.textContent = S.isVideo ? 'Developing footage…' : 'Exposing frame…';
  procBarWrap.classList[S.isVideo?'remove':'add']('hidden');
  procFill.style.width='0%'; procPct.textContent='0%';

  const fname = S.file.filename;
  const fid   = S.selectedCam;
  const camName = S.filters.find(f=>f.id===fid)?.name || fid;

  if(!S.isVideo) {
    try {
      const res = await fetch('/api/process/photo',{
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({filename:fname, filter_id:fid})
      });
      const data = await res.json();
      if(!res.ok) throw new Error(data.error||'Processing failed');
      S.outputFilename = data.output_filename;
      showResult(camName);
    } catch(e) {
      toast(e.message,'error');
      doneProcessing();
    }
  } else {
    try {
      const res = await fetch('/api/process/video',{
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({filename:fname, filter_id:fid})
      });
      const data = await res.json();
      if(!res.ok) throw new Error(data.error||'Video processing failed');
      S.jobId = data.job_id;
      pollJob(data.job_id, camName);
    } catch(e) {
      toast(e.message,'error');
      doneProcessing();
    }
  }
}

function pollJob(jobId, camName) {
  if(S.jobTimer) clearInterval(S.jobTimer);
  S.jobTimer = setInterval(async()=>{
    try {
      const res = await fetch(`/api/process/video/status/${jobId}`);
      const data = await res.json();
      const pct = data.progress||0;
      procFill.style.width = pct+'%';
      procPct.textContent = pct+'%';
      if(data.status==='done') {
        clearInterval(S.jobTimer);
        S.outputFilename = data.output_filename;
        showResult(camName);
      } else if(data.status==='error') {
        clearInterval(S.jobTimer);
        toast('Video processing failed: '+(data.error||''),'error');
        doneProcessing();
      }
    }catch(e){}
  },1500);
}

function showResult(camName) {
  processingOv.classList.add('hidden');
  doneProcessing();

  hudFilterName.textContent = camName;

  if(!S.isVideo) {
    // Show processed image
    previewImg.src = `/api/preview/${S.outputFilename}`;
    // Setup before/after data
    baBefore.src = S.originalSrc;
    baAfter.src = `/api/preview/${S.outputFilename}`;
  } else {
    previewVideo.src = `/api/preview/${S.outputFilename}`;
    toast('Video ready!','success');
  }

  actionDownload.classList.remove('hidden');
  actionPlaceholder.classList.add('hidden');
  dlLink.href = `/api/download/${S.outputFilename}`;
  dlLink.download = S.outputFilename;
}

function doneProcessing() {
  S.processing = false;
}

/* ── Download ───────────────────────────────────────────────────────────── */
actionDownload.addEventListener('click', () => {
  if(!S.outputFilename) return;
  dlLink.href = `/api/download/${S.outputFilename}`;
  dlLink.download = S.outputFilename;
  dlLink.click();
  toast('Saving to downloads…','success');
});

/* ── Before/After compare ───────────────────────────────────────────────── */
btnCompare.addEventListener('click', () => {
  if(!S.outputFilename || S.isVideo) return;
  S.comparing = !S.comparing;
  baWrap.classList.toggle('hidden', !S.comparing);
  if(S.comparing) setSlider(0.5);
});

let dragging = false;
function getSliderPct(cx) {
  const rect = baWrap.getBoundingClientRect();
  return Math.min(Math.max((cx-rect.left)/rect.width, 0.04), 0.96);
}
function setSlider(pct) {
  baAfterClip.style.width = (pct*100)+'%';
  baHandle.style.left = (pct*100)+'%';
}
baHandle.addEventListener('mousedown', e=>{dragging=true;e.preventDefault();});
baHandle.addEventListener('touchstart', e=>{dragging=true;e.preventDefault();},{passive:false});
document.addEventListener('mousemove', e=>{if(dragging)setSlider(getSliderPct(e.clientX));});
document.addEventListener('touchmove', e=>{if(dragging)setSlider(getSliderPct(e.touches[0].clientX));},{passive:true});
document.addEventListener('mouseup', ()=>{dragging=false;});
document.addEventListener('touchend', ()=>{dragging=false;});
// Tap anywhere on slider to move
baWrap.addEventListener('click', e=>{
  if(e.target===baHandle||baHandle.contains(e.target)) return;
  setSlider(getSliderPct(e.clientX));
});

/* ── New media ──────────────────────────────────────────────────────────── */
btnNewMedia.addEventListener('click', resetApp);

function resetApp() {
  if(S.jobTimer) clearInterval(S.jobTimer);
  S.file=null; S.outputFilename=null; S.jobId=null; S.processing=false; S.comparing=false; S.isVideo=false;
  if(S.originalSrc){URL.revokeObjectURL(S.originalSrc);S.originalSrc=null;}
  fileInput.value='';
  mediaPreview.classList.add('hidden');
  uploadZone.classList.remove('hidden');
  uploadInner.classList.remove('hidden');
  uploadProg.classList.add('hidden');
  processingOv.classList.add('hidden');
  baWrap.classList.add('hidden');
  actionDownload.classList.add('hidden');
  actionPlaceholder.classList.remove('hidden');
  hudFilterName.textContent='';
}

/* ── Sample button ──────────────────────────────────────────────────────── */
g('btnSample').addEventListener('click', () => {
  toast('Load your own photo to try filters!','info');
});

/* ── Init ───────────────────────────────────────────────────────────────── */
setSlider(0.5);
