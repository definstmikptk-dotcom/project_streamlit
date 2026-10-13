const G='#66bb6a',Y='#ffd54f',F=(x,d=2)=>(+x).toLocaleString('id-ID',{maximumFractionDigits:d});
const $=id=>document.getElementById(id),charts={};
const lab=c=>c.replace('_',' ');
function mk(id,cfg){if(charts[id])charts[id].destroy();charts[id]=new Chart($(id),cfg)}
const opt=(o={})=>({responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},...o});
fetch('/api/data').then(r=>r.json()).then(d=>{
 const S=c=>d.cols[c].stats,cs=Object.keys(d.cols);
 $('kpis').innerHTML=[['Total Responden',d.n],['Rata-rata Exam Score',F(S('Exam_Score').mean)],['Rata-rata Study Hours',F(S('Study_Hours').mean)],['Rata-rata Attendance',F(S('Attendance').mean)+'%'],['Rata-rata Kepuasan',F(S('Satisfaction').mean)],['Rata-rata Spending','Rp '+F(S('Monthly_Spending').mean,1)]].map(k=>`<div class="k"><small>${k[0]}</small><b>${k[1]}</b></div>`).join('');
 mk('gen',{type:'doughnut',data:{labels:['Perempuan (F)','Laki-laki (M)'],datasets:[{data:[d.gender.F,d.gender.M],backgroundColor:[G,Y]}]},options:opt({plugins:{legend:{display:true,position:'bottom'}}})});
 mk('sat',{type:'bar',data:{labels:d.sat.labels,datasets:[{data:d.sat.values,backgroundColor:G}]},options:opt({scales:{y:{title:{display:true,text:'Frekuensi'}}}})});
 mk('age',{type:'bar',data:{labels:d.age.labels.map(a=>'Usia '+a),datasets:[{data:d.age.values,backgroundColor:Y,borderColor:'#f5b800',borderWidth:1}]},options:opt({scales:{y:{min:0,max:100}}})});
 mk('cor',{type:'bar',data:{labels:d.corr.labels.map(lab),datasets:[{data:d.corr.values,backgroundColor:d.corr.values.map(v=>v>=0?G:Y)}]},options:opt({indexAxis:'y',scales:{x:{min:-1,max:1}}})});
 [$('v1'),$('sx'),$('sy')].forEach((s,i)=>{s.innerHTML=cs.map(c=>`<option value="${c}">${lab(c)}</option>`).join('');s.value=['Study_Hours','Study_Hours','Exam_Score'][i]});
 function one(){const c=$('v1').value,x=d.cols[c],s=x.stats;
  mk('hist',{type:'bar',data:{labels:x.bins,datasets:[{data:x.hist,backgroundColor:G}]},options:opt({scales:{y:{title:{display:true,text:'Frekuensi'}}},plugins:{legend:{display:false},title:{display:true,text:'Distribusi '+lab(c)}}})});
  $('stats').innerHTML=[['mean','Mean'],['median','Median'],['mode','Modus'],['std','Std Dev',1],['var','Variansi'],['range','Range'],['q1','Q1'],['q3','Q3'],['iqr','IQR'],['skew','Skewness'],['cv','CV %'],['outlier','Outlier']].map(a=>`<div class="st${a[2]?' hl':''}"><b>${F(s[a[0]])}</b><span>${a[1]}</span></div>`).join('');
  $('tag').textContent=Math.abs(s.skew)<.5?'Simetris':s.skew>0?'Miring kanan':'Miring kiri'}
 function sc(){const x=$('sx').value,y=$('sy').value,p=d.rows.map(r=>({x:r[x],y:r[y]})),n=p.length,mx=p.reduce((a,b)=>a+b.x,0)/n,my=p.reduce((a,b)=>a+b.y,0)/n;
  let sxy=0,sxx=0,syy=0;p.forEach(q=>{sxy+=(q.x-mx)*(q.y-my);sxx+=(q.x-mx)**2;syy+=(q.y-my)**2});const b=sxy/sxx,a=my-b*mx,r=sxy/Math.sqrt(sxx*syy);
  const x0=Math.min(...p.map(q=>q.x)),x1=Math.max(...p.map(q=>q.x));
  mk('sc',{type:'scatter',data:{datasets:[{data:p,backgroundColor:G,pointRadius:4},{type:'line',data:[{x:x0,y:a+b*x0},{x:x1,y:a+b*x1}],borderColor:'#f5b800',borderWidth:3,pointRadius:0}]},options:opt({scales:{x:{title:{display:true,text:lab(x)}},y:{title:{display:true,text:lab(y)}}}})});
  $('scn').textContent=`Korelasi (r) = ${F(r)} · Garis regresi: ${lab(y)} = ${F(a)} + ${F(b)} × ${lab(x)}`}
 $('v1').onchange=one;$('sx').onchange=$('sy').onchange=sc;one();sc();
 const h=['mean','median','mode','std','var','min','max','range','iqr','skew','cv'],hn=['Mean','Median','Modus','Std Dev','Varians','Min','Max','Range','IQR','Skew','CV %'];
 $('tb').innerHTML='<thead><tr><th>Variabel</th>'+hn.map(x=>`<th>${x}</th>`).join('')+'</tr></thead><tbody>'+cs.map(c=>`<tr><td>${lab(c)}</td>`+h.map(k=>`<td>${F(S(c)[k])}</td>`).join('')+'</tr>').join('')+'</tbody>';
 $('gt').innerHTML='<thead><tr><th>Variabel</th><th>Perempuan (F)</th><th>Laki-laki (M)</th><th>Selisih (F−M)</th></tr></thead><tbody>'+cs.map(c=>`<tr><td>${lab(c)}</td><td>${F(d.gmeans[c].F)}</td><td>${F(d.gmeans[c].M)}</td><td><b>${F(d.gmeans[c].F-d.gmeans[c].M)}</b></td></tr>`).join('')+'</tbody>';
 $('dec').innerHTML=d.insights.map(i=>`<div class="dc${i.t[0]=='⚠'?' warn':''}"><h3>${i.t}</h3><p>${i.d}</p><div class="k2"><b>Keputusan:</b> ${i.k}</div></div>`).join('');
});
