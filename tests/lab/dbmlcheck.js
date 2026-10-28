const {Parser}=require('@dbml/core');const fs=require('fs');
try{const db=new Parser().parse(fs.readFileSync(process.argv[2],'utf8'),'dbml');console.log('VALID: tables',db.schemas.reduce((a,s)=>a+s.tables.length,0),'refs',db.schemas.reduce((a,s)=>a+s.refs.length,0));}
catch(e){const errs=e.diags||[e];console.log('INVALID:',errs.length,'errors');errs.slice(0,6).forEach(d=>console.log(' -',(d.message||String(d)).slice(0,140), d.location?JSON.stringify(d.location.start):''));}
