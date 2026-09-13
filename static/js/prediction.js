const locations=["Guntur","Vijayawada","Visakhapatnam","Tirupati","Nellore","Kurnool","Anantapur","Rajahmundry","Kakinada","Ongole","Kadapa","Srikakulam","Hyderabad","Chennai","Bengaluru","Mumbai","Pune","Delhi"];
const $=id=>document.getElementById(id);
function val(id){return $(id).value}
function money(x){return "₹"+Number(x).toLocaleString("en-IN",{maximumFractionDigits:0})}
function loadLocations(){const s=$("Location");s.innerHTML=locations.map(x=>`<option value="${x}">${x}</option>`).join("");}
async function predict(){
 const data={Location:val("Location"),Area:val("Area"),Bedrooms:val("Bedrooms"),Bathrooms:val("Bathrooms"),Floors:val("Floors"),Property_Age:val("Property_Age"),Parking:val("Parking"),Kitchen:val("Kitchen"),Balcony:val("Balcony"),Furnishing:val("Furnishing"),Property_Type:val("Property_Type"),Construction_Quality:val("Construction_Quality")};
 const btn=$("predictBtn"); const err=$("error"); btn.disabled=true; btn.textContent="⏳ Predicting..."; err.classList.add("d-none");
 try{const r=await fetch("/api/predict",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});const d=await r.json();if(!r.ok)throw new Error(d.error||"Prediction failed");$("result").classList.remove("d-none");$("price").textContent=money(d.price);$("range").textContent=`Estimated range: ${money(d.lower)} – ${money(d.upper)}`;$("market").textContent=money(d.market_average);$("difference").textContent=(d.difference_pct>=0?"+":"")+d.difference_pct.toFixed(1)+"%";if(typeof loadHistory==="function")loadHistory();}catch(e){err.textContent=e.message;err.classList.remove("d-none");}finally{btn.disabled=false;btn.textContent="🤖 Predict House Price";}
}
document.addEventListener("DOMContentLoaded",()=>{loadLocations();$("predictBtn").addEventListener("click",predict);});
