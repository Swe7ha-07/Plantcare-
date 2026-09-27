import {WateringLog,FertilizerLog,HealthRecord} from '../models/index.js';
const DAY=86400000;
const dateOnly=d=>new Date(new Date(d).toISOString().slice(0,10));
export async function careFor(plant,now=new Date()){
 const [water,fert,health]=await Promise.all([WateringLog.findOne({plantId:plant._id}).sort({date:-1}),FertilizerLog.findOne({plantId:plant._id}).sort({dateApplied:-1}),HealthRecord.countDocuments({plantId:plant._id,status:{$in:['Active','Monitoring']}})]);
 const lastWater=water?.date||plant.dateAdded; const nextWater=new Date(new Date(lastWater).getTime()+plant.wateringFrequency*DAY); const daysUntil=Math.ceil((dateOnly(nextWater)-dateOnly(now))/DAY);
 let status=daysUntil<0?'OVERDUE':daysUntil===0?'CARE DUE':daysUntil<=2?'CARE SOON':'CARE OK';
 return {lastWatered:lastWater,nextWatering:nextWater,daysUntilWatering:daysUntil,wateringDue:daysUntil<=0,wateringOverdue:daysUntil<0,lastFertilizer:fert?.dateApplied||null,nextFertilizer:fert?.nextApplication||null,activeHealthIssues:health,status};
}
export async function careMap(plants){return Object.fromEntries(await Promise.all(plants.map(async p=>[String(p._id),await careFor(p)])));}
