const options={xaxis:{show:true,categories:{{chart_data.dates|safe}},labels:{show:true,style:{fontFamily:"Inter, sans-serif",cssClass:'text-xs font-normal fill-gray-500 dark:fill-gray-400'}},axisBorder:{show:false,},axisTicks:{show:false,},},yaxis:{show:true,labels:{show:true,style:{fontFamily:"Inter, sans-serif",cssClass:'text-xs font-normal fill-gray-500 dark:fill-gray-400'},}},series:[{name:"Response time (ms)",data:{{chart_data.data|safe}},color:"#1A56DB",},],chart:{sparkline:{enabled:false},height:"100%",width:"100%",type:"area",fontFamily:"Inter, sans-serif",dropShadow:{enabled:false,},toolbar:{show:false,},},tooltip:{enabled:true,x:{show:true,},},fill:{type:"gradient",gradient:{opacityFrom:0.55,opacityTo:0,shade:"#1C64F2",gradientToColors:["#1C64F2"],},},dataLabels:{enabled:false,},stroke:{width:6,},legend:{show:false},grid:{show:false,},}
if(document.getElementById("labels-chart")&&typeof ApexCharts!=='undefined'){const chart=new ApexCharts(document.getElementById("labels-chart"),options);chart.render();};window.initializeTabs=function(){const tabButtons=document.querySelectorAll('[role="tab"]');const tabPanels=document.querySelectorAll('[role="tabpanel"]');if(tabButtons.length>0){tabButtons[0].setAttribute('aria-selected','true');tabPanels[0].classList.remove('hidden');}
tabButtons.forEach(button=>{button.addEventListener('click',()=>{tabButtons.forEach(btn=>{btn.setAttribute('aria-selected','false');});tabPanels.forEach(panel=>{panel.classList.add('hidden');});button.setAttribute('aria-selected','true');const targetId=button.getAttribute('data-tabs-target').substring(1);document.getElementById(targetId).classList.remove('hidden');});});};;document.addEventListener('DOMContentLoaded',function(){const sidebar=document.getElementById('logo-sidebar');const collapseBtn=document.getElementById('sidebar-collapse-btn');const sidebarTexts=document.querySelectorAll('.sidebar-text');const mainContent=document.getElementById('main-content');const tooltipElements=document.querySelectorAll('[role="tooltip"]');function setSidebarState(collapsed){localStorage.setItem('sidebarCollapsed',collapsed);}
function getSidebarState(){return localStorage.getItem('sidebarCollapsed')==='true';}
function updateSidebarUI(collapsed){if(collapsed){sidebar.classList.remove('w-64');sidebar.classList.add('w-16');sidebarTexts.forEach(text=>text.classList.add('hidden'));mainContent.classList.remove('sm:ml-64');mainContent.classList.add('sm:ml-16');collapseBtn.querySelector('svg').classList.add('rotate-180');tooltipElements.forEach(tooltip=>{tooltip.style.display='block';});}else{sidebar.classList.add('w-64');sidebar.classList.remove('w-16');sidebarTexts.forEach(text=>text.classList.remove('hidden'));mainContent.classList.add('sm:ml-64');mainContent.classList.remove('sm:ml-16');collapseBtn.querySelector('svg').classList.remove('rotate-180');tooltipElements.forEach(tooltip=>{tooltip.style.display='none';});}}
const initialState=getSidebarState();updateSidebarUI(initialState);collapseBtn.addEventListener('click',function(){const newState=!getSidebarState();setSidebarState(newState);updateSidebarUI(newState);});});;